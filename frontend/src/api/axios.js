import axios from 'axios'
// import qs from 'qs'
import { Message } from 'element-ui'
window.axiosPromiseArr = [] // axios中设置放置要取消的对象
    // create an axios instance
const service = axios.create({
    baseURL: process.env.VUE_APP_BASE_API, // url = base url + request url
    // withCredentials: true, // send cookies when cross-domain requests
    timeout: 50000, // request timeout
    headers: {
        Accept: '*/*',
        // 'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        'Content-Type': 'application/json;charset=utf-8'
    },
    transformRequest: [
        function(data, headers) {
            console.log('data', data, headers)
            return data
                // 对 data 进行任意转换处理
                // if (headers['Content-Type'] === 'application/x-www-form-urlencoded;charset=utf-8') { return qs.stringify(data) } else { return data }
        }
    ]
})

// request interceptor
service.interceptors.request.use(
    config => {
        // do something before request is sent
        // if (getToken()) {
        //   // let each request carry token
        //   // ['X-Token'] is a custom headers key
        //   // please modify it according to the actual situation
        //   config.headers['Authorization'] = getToken()
        //   // 发起请求时保存页面所有请求
        //   config.cancelToken = new axios.CancelToken(cancel => {
        //     window.axiosPromiseArr.push({ cancel })
        //   })
        // }
        return config
    },
    error => {
        // do something with request error
        console.log(error) // for debug
        return Promise.reject(error)
    }
)

// response interceptor
service.interceptors.response.use(
    /**
     * If you want to get http information such as headers or status
     * Please return  response => response
     */

    /**
     * Determine the request status by custom code
     * Here is just an example
     * You can also judge the status by HTTP Status Code
     */
    response => {
        const res = response.data
        if (process.server && !response.data.success) {
            console.log('报错API:' + response.config.url)
            console.log('报错id:' + response.config.data)
        }
        return res
    },
    error => {
        if (axios.isCancel(error)) {
            // 为了终结promise链 (实际请求不会走到.catch(rej=>{}),这样就不会触发错误提示之类的)
            return new Promise(() => {})
        }
        if (process.server) { console.log(['Server-side API Error', error.config, error.response]) }
        const message = 'Some unknown errors occurs <br> We will fix them as soon as possible'
            // const status = error.response.status
            // if (status === 401) {
            //     message = 'You have been logged out, you can cancel to stay on this page, or log in again'
            // } else if (status === 403) {
            //     message = error.response.data.detail
            // } else if (status === 404) {
            //     message = 'Some APIs not found <br> We will fix them as soon as possible'
            // } else {
            //     message = 'Some unknown errors occurs <br> We will fix them as soon as possible'
            // }
        Message({
            message: message,
            type: 'error',
            duration: 5 * 1000
        })
        return Promise.reject(error)
    }
)

export default service