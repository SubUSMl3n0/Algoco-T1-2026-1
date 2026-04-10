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

//low y high = left y right = 0 y n-1 de inicio
void mergeSort(vector<int>& arr, int left, int right);
void quickSort(vector<int>& arr, int low, int high);
vector<int> sortArray(vector<int>& arr);

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
    if (argc > 1) {
        string ruta = argv[1];
        string nombreFile = ruta.substr(17);

        ifstream input(ruta);

        if(ruta != "data/array_input/a.txt"){

            int n = procesarFile(nombreFile);

            int aux;
            vector<int> arregloMerge(n), arregloQuick(n), arregloSort(n);
            for(int i = 0; i< n; i++){
                input >> aux;
                arregloMerge[i] = aux;
                arregloQuick[i] = aux;
                arregloSort[i] = aux;
                
            }

            string auxNombreFile = nombreFile;
            auxNombreFile.erase(auxNombreFile.size() - 4);//saca ".txt"

            string nombreMerge = auxNombreFile + "_Merge.txt";
            string nombreQuick = auxNombreFile + "_Quick.txt";
            string nombreSort = auxNombreFile + "_Sort.txt";
            string nombreOut = auxNombreFile + "_out.txt";




            //MERGE - tiempo memoria
            auto t_0Merge = chrono::high_resolution_clock::now();
            long m_0Merge = ObtenerKB();

            mergeSort(arregloMerge,0, n-1);

            long m_1Merge = ObtenerKB();
            auto t_1Merge = chrono::high_resolution_clock::now();
            double tiempoMerge = chrono::duration<double>(t_1Merge - t_0Merge).count();
            long memoriaMerge = (m_1Merge >= m_0Merge) ? (m_1Merge - m_0Merge) : 0;
        
            
            /* PIDE UN PURO OUT, SE QUEDA EL DE sort c++
            //salida merge
            ofstream outfileMerge("data/array_output/" + nombreMerge);
            for(int i =0; i <n; i++){
                outfileMerge << arregloMerge[i];
                if(i != n-1) outfileMerge << " ";
            }
            outfileMerge.close();*/

            //escribe medicion Merge
            escribirMediciones("data/measurements/measurements_" + nombreMerge,tiempoMerge, memoriaMerge);








            // QUICK - tiempo memoria
            auto t_0Quick = chrono::high_resolution_clock::now();
            long m_0Quick = ObtenerKB();

            quickSort(arregloQuick, 0, n - 1);

            long m_1Quick = ObtenerKB();
            auto t_1Quick = chrono::high_resolution_clock::now();
            double tiempoQuick = chrono::duration<double>(t_1Quick - t_0Quick).count();
            long memoriaQuick = (m_1Quick >= m_0Quick) ? (m_1Quick - m_0Quick) : 0;

            /*  PIDE UN PURO OUT, SE QUEDA EL DE sort c++
            //salida quick
            ofstream outfileQuick("data/array_output/" + nombreQuick);
            for(int i = 0; i < n; i++){
                outfileQuick << arregloQuick[i];
                if(i != n - 1) outfileQuick << " ";
            }
            outfileQuick.close();*/

            //escribe medicion Quick
            escribirMediciones("data/measurements/measurements_" + nombreQuick, tiempoQuick, memoriaQuick);







            // SORT - tiempo memoria
            auto t_0Sort = chrono::high_resolution_clock::now();
            long m_0Sort = ObtenerKB();

            sortArray(arregloSort);

            long m_1Sort = ObtenerKB();
            auto t_1Sort = chrono::high_resolution_clock::now();
            double tiempoSort = chrono::duration<double>(t_1Sort - t_0Sort).count();
            long memoriaSort = (m_1Sort >= m_0Sort) ? (m_1Sort - m_0Sort) : 0;

            //salida sort
            ofstream outfileSort("data/array_output/" + nombreOut);
            for(int i = 0; i < n; i++){
                outfileSort << arregloSort[i];
                if(i != n - 1) outfileSort << " ";
            }
            outfileSort.close();

            //escribe medicion Sort
            escribirMediciones("data/measurements/measurements_" + nombreSort, tiempoSort, memoriaSort);
        }

    }
    return 0;
}
