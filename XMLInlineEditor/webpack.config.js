const path = require('path');

module.exports = {
  // The entry point file described above
  entry: './src/index.tsx',
  // The location of the build folder described above
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    libraryTarget: 'umd'
  },
  resolve: {
    extensions: ['.ts', '.tsx', '.js', '.css']
  },
  module: {
    rules: [
      // all files with .ts, .cts, .mts or .tsx extension handled by ts-loader
      { test: /\.([cm]?ts|tsx)$/, loader:'ts-loader'},
      // all files with .css loaded by css-loader
      { 
        test: /\.css$/i,
        use: ['css-loader']
      }
    ],
  },
  externals: ["lexical", /^@lexical\/.+$/],
  // Optional and for development only. This provides the ability to
  // map the built code back to the original source format when debugging.
  devtool: 'eval-source-map',
};
