const path = require('path');

module.exports = {
    entry: {
        index: './src/index.js',
        tags: './src/tags.js'
    },
    output: {
        filename: "[name].bundle.js",
        path: path.resolve(__dirname, "dist")
    },
    watch: false,
    mode: "development"
}