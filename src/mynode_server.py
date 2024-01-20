import os
import os.path as path
import shutil
import socket
import subprocess
import threading
import time


def get_free_port():
  sock = socket.socket()
  sock.bind(('', 0))
  port = sock.getsockname()[1]
  sock.close()
  return port


def enqueue_output(out, node_server_inited):
  for line in iter(out.readline, b''):
    utf8_line = str(line, "utf8")
    print(utf8_line, end="")
    if str(line, "utf8").startswith("[Node] 服务启动完成"):
      node_server_inited[0] = True
  out.close()


def wait_until(somepredicate, timeout, period=0.25, *args, **kwargs):
  mustend = time.time() + timeout
  while time.time() < mustend:
    if somepredicate(*args, **kwargs):
      return True
    time.sleep(period)
  return False


def start_node_server(nodejs_path: str):
  node_server_inited = [False]
  print("[消息] 正在尝试启动 Node.js 服务。")
  node_server_port = str(get_free_port())
  cmd = f"{nodejs_path} {path.join(os.getcwd(), 'src/render.mjs')} {node_server_port} {os.getcwd()}"
  print("[命令调用]", cmd)
  node_server = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  t = threading.Thread(target=enqueue_output, args=(node_server.stdout, node_server_inited))
  t.daemon = True  # 线程随主程序同时退出
  t.start()

  wait_until(lambda: node_server_inited[0] == True, 20)
  if node_server_inited == False:
    node_server.kill()
    print("[错误] Node.js 服务启动失败。")
    exit(0)
  
  return {
    "port": node_server_port,
    "server": node_server,
  }
