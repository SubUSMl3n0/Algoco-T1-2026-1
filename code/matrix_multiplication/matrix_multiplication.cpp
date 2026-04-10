#include <cstdio>
#include <vector>
#include <iostream>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <sys/types.h>

using namespace std;
namespace fs = filesystem;

vector<vector<int>> multiplyNaive(vector<vector<int>> &mat1, 
                vector<vector<int>> &mat2);
vector<vector<int>> multiplyStrassen(vector<vector<int>> &mat1, 
                vector<vector<int>> &mat2);

long ObtenerKB() {
    ifstream status("/proc/self/status");
    string line;
    while (getline(status, line)) {
        if (line.rfind("VmRSS:", 0) == 0) {
            istringstream iss(line);
            string key, unit;
            long valueKB;
            iss >> key >> valueKB >> unit; // VmRSS: <num> kB
            return valueKB;
        }
    }
    return 0;
}

void escribirMediciones(const string& outPath, double seconds, long memoryKB) {
    ofstream out(outPath);
    out << fixed << setprecision(6) << seconds << "\n";
    out << memoryKB << "\n";
}

            
int procesarFile(string nombreFile){
    string aux = "";
    for(char caracter : nombreFile){
        if(caracter != '_'){
            aux += caracter;
        }
        else
            break;
    }
    int n = stoi(aux);
    return n;
}

int main(int argc, char const *argv[])
{
    if (argc > 2) {
        string ruta1 = argv[1];
        string ruta2 = argv[2];
        string nombreFile = ruta1.substr(18);

        ifstream input1(ruta1);
        ifstream input2(ruta2);

        if(ruta1 != "data/matrix_input/a.txt"){

            int n = procesarFile(nombreFile);

            vector<vector<int>> mat1(n, vector<int>(n));
            vector<vector<int>> mat2(n, vector<int>(n));
            for(int i = 0; i< n; i++){
                for(int j = 0; j < n; j++){
                    input1 >> mat1[i][j];
                    input2 >> mat2[i][j];
                }
            }

            string auxNombreFile = nombreFile;
            auxNombreFile.erase(auxNombreFile.size() - 6);//saca "_1.txt"

            string nombreNaive = auxNombreFile + "_Naive.txt";
            string nombreStrassen = auxNombreFile + "_Strassen.txt";





            // NAIVE - tiempo memoria
            auto t_0Naive = chrono::high_resolution_clock::now();
            long m_0Naive = ObtenerKB();

            vector<vector<int>> resNaive = multiplyNaive(mat1, mat2);

            long m_1Naive = ObtenerKB();
            auto t_1Naive = chrono::high_resolution_clock::now();
            double tiempoNaive = chrono::duration<double>(t_1Naive - t_0Naive).count();
            long memoriaNaive = (m_1Naive >= m_0Naive) ? (m_1Naive - m_0Naive) : 0;

            //salida Naive
            ofstream outfileNaive("data/matrix_output/" + nombreNaive);
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    outfileNaive << resNaive[i][j];
                    if (j != n - 1) outfileNaive << " ";
                }
                if (i != n - 1) outfileNaive << "\n";
            }
            outfileNaive.close();

            //escribir medicion en naive
            escribirMediciones("data/measurements/measurements_" + nombreNaive, tiempoNaive, memoriaNaive);







            // STRASSEN - tiempo y memoria
            auto t_0Strassen = chrono::high_resolution_clock::now();
            long m_0Strassen = ObtenerKB();

            vector<vector<int>> resStrassen = multiplyStrassen(mat1, mat2);

            long m1_Strassen = ObtenerKB();
            auto t_1Strassen = chrono::high_resolution_clock::now();
            double tiempoStrassen = chrono::duration<double>(t_1Strassen - t_0Strassen).count();
            long memStrassen = (m1_Strassen >= m_0Strassen) ? (m1_Strassen - m_0Strassen) : 0;

            // salida strassen
            ofstream outfileStrassen("data/matrix_output/" + nombreStrassen);
            for (int i = 0; i < n; i++) {
                for (int j = 0; j < n; j++) {
                    outfileStrassen << resStrassen[i][j];
                    if (j != n - 1) outfileStrassen << " ";
                }
                if (i != n - 1) outfileStrassen << "\n";
            }
            outfileStrassen.close();

            // escribir medicion en strassen
            escribirMediciones("data/measurements/measurements_" + nombreStrassen, tiempoStrassen, memStrassen);

        }
    }
    return 0;
}
