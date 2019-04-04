from tqdm import tqdm
import time

text = ""
for char in tqdm(["a", "b", "c", "d"], ascii=True):
    time.sleep(0.25)
    text = text + char