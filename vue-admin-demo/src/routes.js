import Login from './views/Login.vue'
import NotFound from './views/404.vue'
import Index from './views/Index.vue'
import Home from './views/Home.vue'
import Server from './views/server/Server.vue'
import Service from './views/service/Service.vue'
import Proxy from './views/proxy/Proxy.vue'

let routes = [
    {
        path: '/login',
        component: Login,
        name: '',
        hidden: true
    },
    {
        path: '/404',
        component: NotFound,
        name: '',
        hidden: true
    },
    //{ path: '/main', component: Main },
    {
        path: '/',
        component: Home,
        name: '',
        iconCls: 'el-icon-menu',
        leaf: true,//只有一个节点
        children: [
            { path: '/Index', component: Index, name: '首页' }
        ]
    },
    {
        path: '/',
        component: Home,
        name: '',
        iconCls: 'el-icon-menu',
        leaf: true,//只有一个节点
        children: [
            { path: '/Proxy', component: Proxy, name: '代理服务管理' }
        ]
    },   
    {
        path: '/',
        component: Home,
        name: '',
        iconCls: 'el-icon-menu',
        leaf: true,//只有一个节点
        children: [
            { path: '/Service', component: Service, name: '服务管理' }
        ]
    },    
    {
        path: '/',
        component: Home,
        name: '',
        iconCls: 'el-icon-menu',
        leaf: true,//只有一个节点
        children: [
            { path: '/Server', component: Server, name: '服务器管理' }
        ]
    },  
    {
        path: '*',
        hidden: true,
        redirect: { path: '/404' }
    }
];

export default routes;