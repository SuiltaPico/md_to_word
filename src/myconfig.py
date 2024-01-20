import os.path as path
import toml

def load_config(cfg_path):

  cfg = None
  if cfg_path:
    print("[消息] 加载来自参数的配置文件", cfg_path)
    cfg = toml.load(cfg_path)
  elif path.exists("./private_config.toml"):
    cfg = toml.load("./private_config.toml")
  else:
    cfg = toml.load("./config.toml")

  required_fields = ["src_path", "target_path", "template_path",
                      "temp_dir_path", "nodejs_path", "chromium_path"]
  path_fields = ["src_path", "template_path", "nodejs_path", "chromium_path"]
  marco_fields = ["temp_dir_path"]
  for rf in required_fields:
    if not rf in cfg or cfg[rf] == "":
      raise Exception(f"必填项 {rf} 没有被设置。")
  for mf in marco_fields:
    cfg[mf] = cfg[mf].replace(
      "{src_dir}", path.dirname(path.abspath(cfg["src_path"])))
    cfg[mf] = cfg[mf].replace(
      "{target_dir}", path.dirname(path.abspath(cfg["target_path"])))
  # print(cfg)
  for pf in path_fields:
    if not path.exists(cfg[pf]):
      raise Exception(f"选项 {pf} 的路径 {cfg[pf]} 对应的文件不存在。")

  if not "obsdian_image_find_paths" in cfg:
    cfg["obsdian_image_find_paths"] = []

  return cfg
