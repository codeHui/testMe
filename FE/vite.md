是的，Vite可以将React打包并且生成适用于生产环境和直接在浏览器中打开的HTML文件。 

要使用Vite打包React应用程序，请按照以下步骤操作：

1. 在项目目录下安装React和React DOM依赖项。可以使用npm或yarn工具完成此操作。

2. 安装vite作为开发依赖项（devDependency）。您可以在终端中输入以下命令执行安装操作：

```
npm install vite --save-dev
```

3. 配置vite.config.js文件来设置你的React应用程序相关的选项。配置如下例所示：

```javascript
// vite.config.js
import { defineConfig } from 'vite';
import reactRefresh from '@vitejs/plugin-react-refresh';

export default defineConfig({
  plugins: [reactRefresh()],
});
```

此配置将启用React热重载(Hot Module Replacement)特性，以及其他与React集成相关的功能。

4. 运行以下命令以启动Vite服务器：

```
npm run dev
```

5. 最后，运行以下命令来构建生产版本：

```
npm run build
```

此命令将生成一个dist目录，其中包含您的生产React应用程序的完整打包文件。可以直接从浏览器中打开这些打包文件来访问应用程序。
