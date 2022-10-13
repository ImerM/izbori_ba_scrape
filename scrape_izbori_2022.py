from datetime import datetime
import helper_methods

currentTime = datetime.now().strftime('%Y%m%d%H%M')
folders = helper_methods.generate_folder_structure(currentTime)

election_name = "%22WebResult_2022GENT1_2022_4_20_14_10_43%22"
helper_methods.get_presidency_results_overall(election_name,folders)
helper_methods.get_pred_rs_overall(election_name, folders.predRS)
helper_methods.get_ps_bih_results(election_name, folders.psBiH)
helper_methods.get_parlfbih_results(election_name, folders.pFBiH)
helper_methods.get_nsrs_results(election_name, folders.nsrs)
helper_methods.get_kanton_results_overall(election_name, folders.kantons)
