import os
import wandb
import pytz
from datetime import datetime
import pandas as pd
import json

class WandBLogger:
    """WandB logger."""

    def __init__(self, custom_args, system_prompt):
        self.logger = wandb.init(
            project = "graph-trigger-llms",
            entity='liufanuestc',
            config = {
                "base_model" : custom_args["base_model"],
                "keep_last_n": custom_args["keep_last_n"],
                "system_prompt": system_prompt,
                "n_iter": custom_args["n_iterations"],
                "n_streams": custom_args["n_streams"],

            }
        )

        self.table = pd.DataFrame()
        self.datas = []

    def log(self, args: str, GPT_instructions: dict):

        self.save_to_file(args, GPT_instructions)
    def save_to_file(self, args: str, GPT_instructions):
        path_name = "GPT_Prompts/" + args.base_model + "/"
        file_name =  args.version_name
        file_name = file_name + ".json"
        if not os.path.exists(path_name):
            os.makedirs(path_name)
        with open(path_name + file_name, 'w') as file:
            json.dump(GPT_instructions, file)
    # def log(self,file_name:str, prompt: str, ite: int, improvement: str, edge_index: tuple):
    #
    #
    #     columns = ["Target Node Index", "Prompt", "Improvement", "Edge_index"]
    #     data = [[ite, prompt, improvement, json.dumps(edge_index)]]
    #     self.datas.append(data)
    #
    #
    #     table = wandb.Table(data=data,columns=columns)
    #
    #     wandb.log({'data_table': table})
    def finish(self):
        self.logger.finish()


def save_to_file(args: str, GPT_instructions):
    path_name = "GPT_Prompts/" + args.base_model + "/"
    file_name =  args.file_name
    file_name = file_name + ".json"
    if not os.path.exists(path_name):
        os.makedirs(path_name)
    with open(path_name + file_name, 'w') as file:
        json.dump(GPT_instructions, file)
    

# class Saver:
#     """Saves the conversation."""

#     def __init__(self, args, system_prompt):
#         self.args = args
#         self.system_prompt = system_prompt

#         now = datetime.now(pytz.timezone('US/Eastern'))
#         self.filename = os.path.join(
#             "outputs",
#             f"{args.behavior}",
#             f"output_date_{now.month}_{now.day}_time_{now.hour}_{now.minute}.txt"
#         )

#     def write(self, conv):

#         with open(self.filename, 'w', encoding='utf-8') as f:
#             f.write(f"""
#                 Attack model: {self.args.attack_model_path}
#                 Target model: {self.args.target_model_path}\n
#                 System prompt: \n\n{self.system_prompt}\n\n"""
#             )

#             for counter, (role, s) in enumerate(conv.messages):
#                 if counter % 2 == 1:
#                     f.write(f"""\n{'='*36}
#                         Iteration: {(counter + 1) // 2}
#                         {'='*36}\n
#                         User:\n {s}\n"""
#                     )
#                 else:
#                     f.write(f"Assistant:\n {s}\n")


