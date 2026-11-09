from pathlib import Path
import json

from qiskit import QuantumCircuit

from tools.quito.Quito_CoverageRunning.quito import quito_run


"""
the following commands set the R that rpy2 uses, for each session
for instance, after restarting the command line, we would need to repeat the execution of these commands

export R_HOME="$(R RHOME)"
export RPY2_CFFI_MODE=ABI
"""

QUITO_PATH = Path("tools/quito")
CONFIG_QUITO = Path(QUITO_PATH,"config_quito.json")

def translate_ps(ps_path, num_qubits, meas_qubits):
    with open(ps_path, "r") as f:
        ps_file = json.load(f)  

    if len(ps_file.keys())==2**num_qubits:
        ps_cat="[program_specification_category]\nps_category=full"
    else:
        ps_cat="[program_specification_category]\nps_category=partial"

    ps_str = "[program_specification]\n"
    for in_st, prob_dist in ps_file.items():
        meas_prob = {}
        for val, prob in prob_dist.items():
            val_str=""
            for i in meas_qubits:
                val_str+=str(val[i-(num_qubits-1)])
                meas_prob[val_str] = meas_prob.get(val_str,0) + prob

        for val, prob in meas_prob.items():
            if (len(str(val)))==len(meas_qubits):
                ps_str += f"{in_st},{val}={prob}\n"

    return ps_cat, ps_str

def program_part(input_circuit_path, num_qubits, meas_qubits):
    qubits = ",".join(str(i) for i in range(num_qubits))
    meas_qubits=",".join(str(i) for i in meas_qubits)

    res = f"[program]\nroot={input_circuit_path}\nnum_qubit={num_qubits}\ninputID={qubits}\noutputID={meas_qubits}"

    return res

def quito_config_part():
    with open(CONFIG_QUITO, "r") as f:
        quito_config = json.load(f)

    config = quito_config["quito_configuration"]
    cov_crit = config["coverage_criterion"]
    k = config["K"]
    m = config["M"]
    budget = config["BUDGET"]
    conf_lvl = config["confidence_level"]
    stat_test = config["statistical_test"]
    
    return f"[quito_configuration]\ncoverage_criterion={cov_crit}\nK={k}\nM={m}\nBUDGET={budget}\nconfidence_level={conf_lvl}\nstatistical_test={stat_test}"
    


def build_quito_config(input_circuit_path = "./data/qc/ent.qasm",
                       ps_path = "./data/ps/ent.json",
                       output_path = './data/results/quito/'):
    """
    we assume ./ to be folder tool_model
    this function translates the information from config.json (in the folder tool_model) to a .ini file used by Quito
    most of the information in config.json is used to automatically create the .ini
    however, there are some Quito settings, specifically the ones regarding the *quito_configuration* field, that are not in config.json
    for those settings, the user can modify the file config_quito.json (./tools/quito)
    """
    #build a folder for quito data made from our resources
    data_folder = Path(QUITO_PATH,"data")
    qc_name = ps_path.split("/")[-1].replace(".json","")
    ini_file = Path(data_folder, qc_name + ".ini")
    result_folder = Path(output_path+"/quito")
    if not data_folder.exists():
        data_folder.mkdir()
    if not result_folder.exists():
        result_folder.mkdir()
    # if ini_file.exists():
    #     return ini_file

    qc = QuantumCircuit.from_qasm_file(input_circuit_path)
    # print(qc)
    num_qubits = qc.num_qubits
    meas_qubits = []
    for instruction in qc.data:
        if instruction.operation.name == 'measure':
            for q in instruction.qubits:
                meas_qubits.append(qc.find_bit(q).index)
    #program
    p1 = program_part(input_circuit_path, num_qubits, meas_qubits)

    #program_specification and program_specification_category
    if ps_path is None:
        p2 = "[program_specification_category]\nps_category=no"
    else:
        ps_cat, ps_str = translate_ps(ps_path, num_qubits, meas_qubits)

    #quito_configuration
    p3 = quito_config_part() 

    res = p1+"\n\n"+ps_cat+"\n\n"+ps_str+"\n\n"+p3
    # print(res)
    with open(ini_file, "w") as f:
        f.write(res)

    return ini_file

def exec_quito(input_circuit_path = "./data/qc/ent_mut2.qasm",
               ps_path = "./data/ps/ent.json",
               output_path = './data/results/quito/'):
    
    ini_file = build_quito_config(input_circuit_path, ps_path, output_path)
    quito_run(root_con=ini_file)
    #print(quito_run(root_con=ini_file))
    #quito_run(root_con="./tools/quito/data/swap_test.ini")

#exec_quito()