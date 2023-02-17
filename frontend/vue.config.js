// module.exports = {
//     devServer: {
//         proxy: {
//             '/api': {     //这里最好有一个 /
//                 target: 'https://zhongshihua.acemap.cn',  // 后台接口域名
//                 changeOrigin: true,  //是否跨域
//                 pathRewrite:{
//                     '^/api':''
//                 }
//             }
//         }
//         // before: require('./mock/mock-server.js')
//     }
// }