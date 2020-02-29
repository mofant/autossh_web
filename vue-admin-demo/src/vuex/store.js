import Vue from 'vue'
import Vuex from 'vuex'
import * as actions from './actions'
import * as getters from './getters'

Vue.use(Vuex)

// 应用初始状态
const state = {
    count: 10,
    token: '',
}

// 定义所需的 mutations
const mutations = {
    INCREMENT(state) {
        state.count++
    },
    DECREMENT(state) {
        state.count--
    },
    set_token(state,ltoken) {   //第一个参数是拿到state对象
        localStorage.setItem('token',ltoken);
        state.token = ltoken;
    },
    del_token(state) {
        localStorage.removeItem('token');
        state.token = '';
    },
}

// 创建 store 实例
export default new Vuex.Store({
    actions,
    getters,
    state,
    mutations
})


