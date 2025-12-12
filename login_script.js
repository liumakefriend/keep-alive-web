// 文件名: login_script.js
const puppeteer = require('puppeteer-extra');
// 加载隐身插件，试图绕过 Cloudflare
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

(async () => {
  console.log("🚀 启动隐身浏览器...");
  
  const browser = await puppeteer.launch({
    headless: "new", // 使用新版无头模式
    args: [
      '--no-sandbox', 
      '--disable-setuid-sandbox',
      '--window-size=1920,1080',
      '--disable-blink-features=AutomationControlled' // 禁用自动化特征
    ]
  });

  const page = await browser.newPage();
  
  // 伪装 User-Agent (假装是 Win10 Chrome)
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36');

  // 1. 访问登录页面
  const loginUrl = 'https://betadash.lunes.host/login'; // 假设登录页是这个，如果不是请修改
  console.log(`🌐 正在前往登录页: ${loginUrl}`);
  
  try {
    await page.goto(loginUrl, { waitUntil: 'networkidle2', timeout: 60000 });
  } catch (e) {
    console.error("❌ 页面加载超时，可能被 Cloudflare 拦截。");
    await page.screenshot({ path: 'step1_load_fail.png' });
    await browser.close();
    process.exit(1);
  }

  // 2. 简单的 Cloudflare 等待逻辑
  console.log("🛡️ 等待 5 秒，让 Cloudflare 五秒盾自动通过...");
  await new Promise(r => setTimeout(r, 5000));

  // 截图查看是否卡在盾上
  await page.screenshot({ path: 'step2_pre_login.png' });

  // --- 开始替换的部分 ---

  try {
    console.log("⌨️ 正在输入账号密码...");
    
    // 1. 输入账号 (根据你的截图 image_af030d.png，ID是 email)
    await page.waitForSelector('#email', { visible: true, timeout: 5000 });
    await page.type('#email', process.env.LUNES_EMAIL, { delay: 100 });
    
    // 2. 输入密码 (ID是 password)
    await page.type('#password', process.env.LUNES_PASSWORD, { delay: 120 });

    console.log("🛡️ 检查 Cloudflare 验证码...");
    
    // 尝试寻找 Cloudflare 的 iframe 并点击（如果有的话）
    // 这一步是为了解决截图 image_af0618.png 中的 Turnstile 验证
    try {
        // 查找可能存在的 Cloudflare checkbox iframe
        const frame = page.frames().find(f => f.url().includes('challenge-platform'));
        if (frame) {
            console.log("Found Cloudflare iframe, attempting to click...");
            await frame.click('body');
            await new Promise(r => setTimeout(r, 3000)); // 点完等 3 秒
        }
    } catch (err) {
        console.log("未检测到需要点击的验证码，或自动通过。");
    }

    console.log("🖱️ 点击登录按钮...");
    
    // 3. 点击 'Continue to dashboard' 按钮
    // 使用 XPath 定位包含特定文字的按钮，这比 css selector 更准
    const submitButton = await page.waitForSelector('xpath=//button[contains(., "Continue to dashboard")]', { timeout: 5000 });
    
    await Promise.all([
      submitButton.click(),
      page.waitForNavigation({ waitUntil: 'networkidle2', timeout: 60000 }),
    ]);
    
    console.log("✅ 登录动作完成，正在跳转...");

  } catch (e) {
    console.error("❌ 登录步骤出错：", e.message);
    // 截图保存案发与现场
    await page.screenshot({ path: 'step3_login_error.png' });
    await browser.close();
    process.exit(1);
  }

  // --- 替换结束 ---

  // 4. 访问目标服务器详情页
  const targetUrl = process.env.TARGET_URL;
  console.log(`🚀 跳转到服务器详情页: ${targetUrl}`);
  
  try {
    await page.goto(targetUrl, { waitUntil: 'domcontentloaded', timeout: 30000 });
    // 截图最终状态
    await page.screenshot({ path: 'step4_final_page.png' });
  } catch (e) {
    console.log("⚠️ 跳转详情页超时，尝试直接分析当前页面...");
  }

  // 5. 抓取数据 (UUID/CPU/Plan)
  const bodyText = await page.body().innerText();
  const data = {};

  // 正则匹配
  const uuidMatch = bodyText.match(/UUID\s+([a-z0-9]+)/i);
  const planMatch = bodyText.match(/Plan\s*\n\s*(.+)/i);
  const memoryMatch = bodyText.match(/Memory\s*\n\s*([0-9]+\s*MB)/i);
  const cpuMatch = bodyText.match(/CPU\s*\n\s*([0-9]+%)/i);

  if (uuidMatch) data.UUID = uuidMatch[1];
  if (planMatch) data.Plan = planMatch[1];
  if (memoryMatch) data.Memory = memoryMatch[1];
  if (cpuMatch) data.CPU = cpuMatch[1];

  if (data.UUID) {
    console.log("🎉 【成功】已进入后台，服务器在线！");
    console.table(data);
  } else {
    console.error("⚠️ 【失败】未能提取到 UUID。");
    console.log("可能原因：1. 登录被拦截 2. 需要二次验证 3. 页面布局改变");
    // 强制报错以便 Action 显示红色叉号
    process.exit(1); 
  }

  await browser.close();
})();
