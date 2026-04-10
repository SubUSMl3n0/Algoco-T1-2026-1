from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


FILENAME_PATTERN = re.compile(
	r"^measurements_(\d+)_(aleatorio|ascendente|descendente)_(D1|D7)_([abc])_(Merge|Quick|Sort)\.txt$"
)

ORDER_VALUES = ["aleatorio", "ascendente", "descendente"]
DOMAIN_VALUES = ["D1", "D7"]
ALGORITHM_VALUES = ["Merge", "Quick", "Sort"]
TESTCASE_VALUES = ["a", "b", "c"]
TIME_LABEL = "Tiempo (s)"
MEMORY_LABEL = "Memoria (KB)"


@dataclass
class Measurement:
	size: int
	order: str
	domain: str
	testcase: str
	algorithm: str
	time_sec: float
	memory_kb: float


def parse_filename(file_name: str) -> tuple[int, str, str, str, str] | None:
	match = FILENAME_PATTERN.match(file_name)
	if not match:
		return None

	size = int(match.group(1))
	order = match.group(2)
	domain = match.group(3)
	testcase = match.group(4)
	algorithm = match.group(5)
	return size, order, domain, testcase, algorithm


def load_measurements(measurements_dir: Path) -> tuple[list[Measurement], list[str], list[str]]:
	measurements: list[Measurement] = []
	skipped_files: list[str] = []
	failed_files: list[str] = []

	for file_path in sorted(measurements_dir.glob("*.txt")):
		parsed = parse_filename(file_path.name)
		if parsed is None:
			skipped_files.append(file_path.name)
			continue

		try:
			lines = [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]
			if len(lines) < 2:
				raise ValueError("expected 2 non-empty lines")

			time_sec = float(lines[0])
			memory_kb = float(lines[1])
		except (OSError, ValueError) as exc:
			failed_files.append(f"{file_path.name}: {exc}")
			continue

		size, order, domain, testcase, algorithm = parsed
		measurements.append(
			Measurement(
				size=size,
				order=order,
				domain=domain,
				testcase=testcase,
				algorithm=algorithm,
				time_sec=time_sec,
				memory_kb=memory_kb,
			)
		)

	return measurements, skipped_files, failed_files


def collect_algorithm_averages_for_context(
	measurements: list[Measurement],
	size: int,
	order: str,
	domain: str,
) -> dict[str, tuple[float, float]]:
	averages: dict[str, tuple[float, float]] = {}
	for algorithm in ALGORITHM_VALUES:
		filtered = [
			m for m in measurements
			if m.size == size and m.order == order and m.domain == domain and m.algorithm == algorithm
		]
		if not filtered:
			continue

		avg_time = sum(m.time_sec for m in filtered) / len(filtered)
		avg_memory = sum(m.memory_kb for m in filtered) / len(filtered)
		averages[algorithm] = (avg_time, avg_memory)

	return averages


def plot_by_size_averaging_testcases(measurements: list[Measurement], plots_dir: Path) -> list[Path]:
	created_plots: list[Path] = []
	algorithm_axis_values = ["Quick", "Merge", "Sort"]
	algorithm_positions = {algorithm: index for index, algorithm in enumerate(algorithm_axis_values)}
	order_offsets = {"aleatorio": -0.25, "ascendente": 0.0, "descendente": 0.25}
	order_hatches = {"aleatorio": "//", "ascendente": "xx", "descendente": ".."}
	order_labels = {
		"aleatorio": "promedio aleatorio",
		"ascendente": "promedio ascendente",
		"descendente": "promedio descendente",
	}

	sizes = sorted({item.size for item in measurements})
	for size in sizes:
		fig, axes = plt.subplots(nrows=len(DOMAIN_VALUES), ncols=2, figsize=(14, 8), constrained_layout=True)

		if len(DOMAIN_VALUES) == 1:
			axes = [axes]

		for row_index, domain in enumerate(DOMAIN_VALUES):
			ax_time = axes[row_index][0]
			ax_memory = axes[row_index][1]

			for order in ORDER_VALUES:
				algorithm_values = collect_algorithm_averages_for_context(
					measurements=measurements,
					size=size,
					order=order,
					domain=domain,
				)

				x_values: list[float] = []
				y_times: list[float] = []
				y_memories: list[float] = []

				for algorithm in algorithm_axis_values:
					avg_values = algorithm_values.get(algorithm)
					if avg_values is None:
						continue

					x_values.append(algorithm_positions[algorithm] + order_offsets[order])
					y_times.append(avg_values[0])
					y_memories.append(avg_values[1])

				if not x_values:
					continue

				ax_time.bar(
					x_values,
					y_times,
					width=0.22,
					color="#57c7ff",
					edgecolor="black",
					linewidth=0.8,
					hatch=order_hatches[order],
					label=order_labels[order],
				)
				ax_memory.bar(
					x_values,
					y_memories,
					width=0.22,
					color="#ff9f43",
					edgecolor="black",
					linewidth=0.8,
					hatch=order_hatches[order],
					label=order_labels[order],
				)

			for axis in (ax_time, ax_memory):
				axis.set_xticks([0, 1, 2])
				axis.set_xticklabels(algorithm_axis_values)
				axis.grid(True, linestyle="--", alpha=0.3, axis="y")

			ax_time.set_title(f"{domain} | Tiempo", fontsize=11)
			ax_time.set_ylabel(TIME_LABEL)
			ax_time.legend(loc="best", fontsize=9)

			ax_memory.set_title(f"{domain} | Memoria", fontsize=11)
			ax_memory.set_ylabel(MEMORY_LABEL)
			ax_memory.legend(loc="best", fontsize=9)

			if row_index == len(DOMAIN_VALUES) - 1:
				ax_time.set_xlabel("Algoritmo")
				ax_memory.set_xlabel("Algoritmo")

		output_path = plots_dir / f"sorting_plots_size_{size}_by_algorithm_type_avg_cases.png"
		fig.savefig(output_path, dpi=180)
		plt.close(fig)
		created_plots.append(output_path)

	return created_plots


def compute_average_summary(measurements: list[Measurement]) -> dict[int, dict[str, tuple[float, float]]]:
	summary: dict[int, dict[str, tuple[float, float]]] = {}
	for size in sorted({item.size for item in measurements}):
		summary[size] = {}
		for algorithm in ALGORITHM_VALUES:
			filtered = [m for m in measurements if m.size == size and m.algorithm == algorithm]
			if not filtered:
				continue

			avg_time = sum(m.time_sec for m in filtered) / len(filtered)
			avg_memory = sum(m.memory_kb for m in filtered) / len(filtered)
			summary[size][algorithm] = (avg_time, avg_memory)

	return summary


def plot_average_summary_by_size(summary: dict[int, dict[str, tuple[float, float]]], plots_dir: Path) -> list[Path]:
	created_plots: list[Path] = []
	x_positions = list(range(len(ALGORITHM_VALUES)))

	for size, algo_values in summary.items():
		times = [algo_values.get(algorithm, (0.0, 0.0))[0] for algorithm in ALGORITHM_VALUES]
		memories = [algo_values.get(algorithm, (0.0, 0.0))[1] for algorithm in ALGORITHM_VALUES]

		fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 4.8), constrained_layout=True)
		fig.suptitle(f"Resumen promedio para size={size}", fontsize=14)

		axes[0].bar(x_positions, times, width=0.6, color="#57c7ff", edgecolor="black", linewidth=0.8)
		axes[0].set_title("Tiempo promedio")
		axes[0].set_xticks(x_positions)
		axes[0].set_xticklabels(ALGORITHM_VALUES)
		axes[0].set_xlabel("Algoritmo")
		axes[0].set_ylabel(TIME_LABEL)
		axes[0].grid(True, linestyle="--", alpha=0.3, axis="y")

		axes[1].bar(x_positions, memories, width=0.6, color="#ff9f43", edgecolor="black", linewidth=0.8)
		axes[1].set_title("Memoria promedio")
		axes[1].set_xticks(x_positions)
		axes[1].set_xticklabels(ALGORITHM_VALUES)
		axes[1].set_xlabel("Algoritmo")
		axes[1].set_ylabel(MEMORY_LABEL)
		axes[1].grid(True, linestyle="--", alpha=0.3, axis="y")

		output_path = plots_dir / f"sorting_summary_size_{size}.png"
		fig.savefig(output_path, dpi=180)
		plt.close(fig)
		created_plots.append(output_path)

	return created_plots


def main() -> None:
	script_dir = Path(__file__).resolve().parent
	sorting_dir = script_dir.parent
	measurements_dir = sorting_dir / "data" / "measurements"
	plots_dir = sorting_dir / "data" / "plots"
	plots_dir.mkdir(parents=True, exist_ok=True)

	measurements, _, _ = load_measurements(measurements_dir)
	if not measurements:
		return

	plot_by_size_averaging_testcases(measurements, plots_dir)
	summary = compute_average_summary(measurements)
	plot_average_summary_by_size(summary, plots_dir)
	print("gráficos generados")


if __name__ == "__main__":
	main()
