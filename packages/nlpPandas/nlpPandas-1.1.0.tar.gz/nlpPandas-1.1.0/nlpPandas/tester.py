import helper
import pandas as pd

nlp_pandas = helper.pass_data(pd.read_csv('sampler/onestopenglish.csv'),target_column="Text")

new_df = nlp_pandas.use_preprocessor(preprocessor = "custom", custom = ["P_G_WA1", "P_R_nan", "P_R_web", "P_R_@@@", "P_R_\\n", "P_R_WWW", "P_R_???"], special_token = ["[PAR]"])
new_df.to_csv("sampler/processed_onestopenglish.csv", index = False)

output = nlp_pandas.use_analyzer("base")