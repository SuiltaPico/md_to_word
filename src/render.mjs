// import puppeteer from "puppeteer";
import { run } from "../mermaid-cli/mermaid-cli.mjs";
import express from "express";

const port = process.argv[2];
const cwd = process.argv[3];

const app = express();
const puppeteer_config = {
  headless: 1,
  executablePath: "./chrome/chrome.exe",
};

app.get("/render_mermaid", async (req, res) => {
  console.log(
    `[Node] 执行渲染 Mermaid 任务：${req.query.src} ${req.query.target}`
  );
  console.time("[Node] 渲染 Mermaid 任务");

  await run(req.query.src, req.query.target, {
    puppeteerConfig: puppeteer_config,
    quiet: true,
    outputFormat: "png",
    parseMMDOptions: {},
  });

  console.timeEnd("[Node] 渲染 Mermaid 任务");

  res.status(200);
  res.end();
});

app.listen(port, () => {
  console.log(`[Node] 服务启动完成，在端口 ${port} 上运行。`);
});
