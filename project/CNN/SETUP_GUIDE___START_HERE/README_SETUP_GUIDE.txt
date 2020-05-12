conda create --name PythonGPU                   // or for CPU : conda create --name PythonCPU

conda activate PythonGPU                        // or for CPU : conda activate  PythonCPU

conda install python=3.6

//Verifiez que vous avez bien la bonne version : 
python --version

conda install -c anaconda keras-gpu             // or for CPU : conda install -c anaconda keras

conda install -c conda-forge scikit-image       // maybe this one is not necessary
conda install --file install2.txt

conda install jupyter notebook


