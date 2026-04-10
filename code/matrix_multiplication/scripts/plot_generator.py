from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import matplotlib.pyplot as plt


FILENAME_PATTERN = re.compile(
	r"^measurements_(\d+)_(densa|diagonal|dispersa)_(D0|D10)_([abc])_(Naive|Strassen)\.txt$"
)

KIND_VALUES = ["densa", "diagonal", "dispersa"]
DOMAIN_VALUES = ["D0", "D10"]
ALGORITHM_VALUES = ["Naive", "Strassen"]
TESTCASE_VALUES = ["a", "b", "c"]
TIME_LABEL = "Tiempo (s)"
MEMORY_LABEL = "Memoria (KB)"


@dataclass
class Measurement:
	size: int
	kind: str
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
	kind = match.group(2)
	domain = match.group(3)
	testcase = match.group(4)
	algorithm = match.group(5)
	return size, kind, domain, testcase, algorithm


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

		size, kind, domain, testcase, algorithm = parsed
		measurements.append(
			Measurement(
				size=size,
				kind=kind,
				domain=domain,
				testcase=testcase,
				algorithm=algorithm,
				time_sec=time_sec,
				memory_kb=memory_kb,
			)
		)

	return measurements, skipped_files, failed_files


def collect_kind_averages_for_domain_context(
	measurements: list[Measurement],
	size: int,
	domain: str,
) -> dict[tuple[str, str], tuple[float, float]]:
	averages: dict[tuple[str, str], tuple[float, float]] = {}

	for algorithm in ALGORITHM_VALUES:
		for kind in KIND_VALUES:
			filtered = [
				m for m in measurements
				if m.size == size
				and m.domain == domain
				and m.algorithm == algorithm
				and m.kind == kind
				and m.testcase in TESTCASE_VALUES
			]
			if not filtered:
				continue

			avg_time = sum(m.time_sec for m in filtered) / len(filtered)
			avg_memory = sum(m.memory_kb for m in filtered) / len(filtered)
			averages[(algorithm, kind)] = (avg_time, avg_memory)

	return averages


def plot_by_size(measurements: list[Measurement], plots_dir: Path) -> list[Path]:
	created_plots: list[Path] = []

	base_positions = list(range(len(ALGORITHM_VALUES)))
	kind_offsets = {"densa": -0.25, "diagonal": 0.0, "dispersa": 0.25}
	kind_colors = {"densa": "#57c7ff", "diagonal": "#7bed9f", "dispersa": "#ff9f43"}
	width = 0.22

	sizes = sorted({item.size for item in measurements})
	for size in sizes:
		# 2 filas (D0, D10) x 2 columnas (Tiempo, Memoria)
		fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(14, 9), constrained_layout=True)
		fig.suptitle(
			f"Comparacion por algoritmo (promedio casos a,b,c) para size={size}",
			fontsize=16,
		)

		for row_index, domain in enumerate(DOMAIN_VALUES):
			ax_time = axes[row_index][0]
			ax_memory = axes[row_index][1]

			averages = collect_kind_averages_for_domain_context(
				measurements=measurements,
				size=size,
				domain=domain,
			)

			for kind in KIND_VALUES:
				x_values = [x + kind_offsets[kind] for x in base_positions]
				y_time = [averages.get((algorithm, kind), (0.0, 0.0))[0] for algorithm in ALGORITHM_VALUES]
				y_memory = [averages.get((algorithm, kind), (0.0, 0.0))[1] for algorithm in ALGORITHM_VALUES]

				ax_time.bar(
					x_values, y_time, width=width, color=kind_colors[kind],
					edgecolor="black", linewidth=0.8, label=kind
				)
				ax_memory.bar(
					x_values, y_memory, width=width, color=kind_colors[kind],
					edgecolor="black", linewidth=0.8, label=kind
				)

			ax_time.set_title(f"{domain} | Tiempo", fontsize=11)
			ax_time.set_xticks(base_positions)
			ax_time.set_xticklabels(ALGORITHM_VALUES)
			ax_time.set_ylabel(TIME_LABEL)
			ax_time.grid(True, linestyle="--", alpha=0.3, axis="y")
			ax_time.legend(loc="best", fontsize=9)

			ax_memory.set_title(f"{domain} | Memoria", fontsize=11)
			ax_memory.set_xticks(base_positions)
			ax_memory.set_xticklabels(ALGORITHM_VALUES)
			ax_memory.set_ylabel(MEMORY_LABEL)
			ax_memory.grid(True, linestyle="--", alpha=0.3, axis="y")
			ax_memory.legend(loc="best", fontsize=9)

			if row_index == len(DOMAIN_VALUES) - 1:
				ax_time.set_xlabel("Algoritmo")
				ax_memory.set_xlabel("Algoritmo")

		output_path = plots_dir / f"matrix_plots_size_{size}_by_algorithm_kind_avg_cases.png"
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

		output_path = plots_dir / f"matrix_summary_size_{size}.png"
		fig.savefig(output_path, dpi=180)
		plt.close(fig)
		created_plots.append(output_path)

	return created_plots


def should_create_combined_summary(summary: dict[int, dict[str, tuple[float, float]]]) -> bool:
	for algo_values in summary.values():
		if not algo_values:
			continue
		max_time = max(values[0] for values in algo_values.values())
		if max_time < 0.01:
			return True
	return False


def plot_combined_average_summary(summary: dict[int, dict[str, tuple[float, float]]], plots_dir: Path) -> Path | None:
	sizes = sorted(summary.keys())
	if not sizes:
		return None

	x_positions = list(range(len(ALGORITHM_VALUES)))
	fig, axes = plt.subplots(nrows=len(sizes), ncols=2, figsize=(12, 3.8 * len(sizes)), constrained_layout=True)
	fig.suptitle("Resumen promedio combinado por tamano", fontsize=16)

	if len(sizes) == 1:
		axes = [axes]

	for row_index, size in enumerate(sizes):
		algo_values = summary[size]
		times = [algo_values.get(algorithm, (0.0, 0.0))[0] for algorithm in ALGORITHM_VALUES]
		memories = [algo_values.get(algorithm, (0.0, 0.0))[1] for algorithm in ALGORITHM_VALUES]

		ax_time = axes[row_index][0]
		ax_memory = axes[row_index][1]

		ax_time.bar(x_positions, times, width=0.6, color="#57c7ff", edgecolor="black", linewidth=0.8)
		ax_time.set_title(f"Size {size} | Tiempo promedio")
		ax_time.set_xticks(x_positions)
		ax_time.set_xticklabels(ALGORITHM_VALUES)
		ax_time.set_ylabel(TIME_LABEL)
		ax_time.grid(True, linestyle="--", alpha=0.3, axis="y")

		ax_memory.bar(x_positions, memories, width=0.6, color="#ff9f43", edgecolor="black", linewidth=0.8)
		ax_memory.set_title(f"Size {size} | Memoria promedio")
		ax_memory.set_xticks(x_positions)
		ax_memory.set_xticklabels(ALGORITHM_VALUES)
		ax_memory.set_ylabel(MEMORY_LABEL)
		ax_memory.grid(True, linestyle="--", alpha=0.3, axis="y")

		if row_index == len(sizes) - 1:
			ax_time.set_xlabel("Algoritmo")
			ax_memory.set_xlabel("Algoritmo")

	output_path = plots_dir / "matrix_summary_all_sizes.png"
	fig.savefig(output_path, dpi=180)
	plt.close(fig)
	return output_path


def main() -> None:
	script_dir = Path(__file__).resolve().parent
	matrix_dir = script_dir.parent
	measurements_dir = matrix_dir / "data" / "measurements"
	plots_dir = matrix_dir / "data" / "plots"
	plots_dir.mkdir(parents=True, exist_ok=True)

	measurements, _, _ = load_measurements(measurements_dir)
	if not measurements:
		return

	plot_by_size(measurements, plots_dir)
	summary = compute_average_summary(measurements)
	plot_average_summary_by_size(summary, plots_dir)
	if should_create_combined_summary(summary):
		plot_combined_average_summary(summary, plots_dir)

	print("gráficos generados")


if __name__ == "__main__":
	main()
