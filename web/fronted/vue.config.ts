import {defineConfig} from '@vue/cli-service'

export default defineConfig({
    transpileDependencies: true,
    publicPath: '/',
    outputDir: 'dist',
    assetsDir: 'static',
    lintOnSave: false,
    productionSourceMap: false,
    devServer: {
        port: 8080,
        proxy: {
            '/api': {
                target: 'http://localhost:3033',
                changeOrigin: true,
                secure: false
            }
        }
    },
    configureWebpack: {
        optimization: {
            splitChunks: {
                chunks: 'all',
                cacheGroups: {
                    vendor: {
                        name: 'chunk-vendors',
                        test: /[\\/]node_modules[\\/]/,
                        priority: 10,
                        chunks: 'initial'
                    },
                    common: {
                        name: 'chunk-common',
                        minChunks: 2,
                        priority: 5,
                        chunks: 'initial'
                    }
                }
            }
        }
    }
})

