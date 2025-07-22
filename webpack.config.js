const path = require('path');
const { VueLoaderPlugin } = require('vue-loader'); // 🔹 Agregamos VueLoaderPlugin

module.exports = {
  entry: './frontend/src/main.js',
  output: {
    path: path.resolve(__dirname, 'skylimit/static/js'),
    filename: 'bundle.js'
  },
  module: {
    rules: [
      {
        test: /\.vue$/,
        loader: 'vue-loader',
      },
      {
        test: /\.js$/,
        loader: 'babel-loader',
        exclude: /node_modules/,
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      }
    ]
  },
  resolve: {
    alias: {
      vue$: 'vue/dist/vue.esm.js',
    },
    extensions: ['*', '.js', '.vue', '.json']
  },
  plugins: [
    new VueLoaderPlugin() // 🔹 Agregamos el plugin aquí
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'skylimit/static'),
    },
    compress: true,
    port: 8080
  }
};
