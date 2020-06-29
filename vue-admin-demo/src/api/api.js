import axios from 'axios';
import store from '../vuex/store'
import { Message } from 'element-ui'
// import * as axios from './axios';

axios.interceptors.request.use(function(config) {

    let token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = "JWT " + token;
    }
    return config;
}, function(error) {
    return Promise.reject(error);
});

axios.interceptors.response.use(response => {

    return response;
    }, error => {
        if (error.response.status == 401) {
            localStorage.clear(); 
            Message({
                message: 'token失效,请重新登录!',
                type: 'warning',
                center: true,
                // onClose:function () {
                //     console.log('关闭了看下');
                //     router.push({
                //         path: '/login',
                //     });
                // }
            });
        }
    return Promise.reject(error) //返回接口返回的错误信息
})

let base = '';

let api = "/api"

export const requestLogin = params => { return axios.post('/api/token/', params).then(res => res.data); };


// gov user模块
export const getRoleUserList = params => {return axios.get(`${api}/gov/user/list`, { params: params}); };
export const modifyGovUser = params => { return axios.put(`${api}/gov/user`, params ); };
export const addGovUser = params => { return axios.post(`${api}/gov/user`,  params ); };
export const delGovUser = params => { return axios.delete(`${api}/gov/user`, { params: params}); };
export const batchDel = params => { return axios.put(`${api}/gov/user/list`,  params ); };


// server 接口
export const getServerList = params => { return axios.get(`${api}/servers/`, { params }); };
export const createServer = params => { return axios.post(`${api}/servers/`, params); };
export const modifyServer = params => { return axios.put(`${api}/server/${params.id}`, params); };
export const delServer = params => { return axios.delete(`${api}/server/${params.id}`, params); };


// service接口
export const getServiceList = params => { return axios.get(`${api}/services/`, { params }); };
export const createService = params => { return axios.post(`${api}/services/`, params ); };
export const modifyService = params => { return axios.put(`${api}/service/${params.id}`, params ); };
export const delService = params => { return axios.delete(`${api}/service/${params.id}`, params ); };


// proxy 接口
export const getProxyList = params => { return axios.get(`${api}/proxys/`, { params }); };
export const createProxy = params => { return axios.post(`${api}/proxys/`,  params ); };
export const modifyProxy = params => { return axios.put(`${api}/proxy/${params.id}`, params ); };
export const delProxy = params => { return axios.delete(`${api}/proxy/${params.id}`, params ); };


// proxy 控制接口
export const refreshProxy = params => { return axios.get(`${api}/proxy/service/${params.id}`, params ); };
export const startProxy = params => { return axios.post(`${api}/proxy/service/${params.id}`, params ); };
export const stopProxy = params => { return axios.put(`${api}/proxy/service/${params.id}`, params ); };
export const deleteProxy = params => { return axios.delete(`${api}/proxy/service/${params.id}`, params ); };