import Login from '../views/login_system'
import Register from '../views/register'
import FindPsd from '../views/FindPsd'
import Setting from '../views/Setting'
import ChangePsd from '../views/ChangePsd'
import FeedBack from '../views/FeedBack'
import SetInformation from '..//views/SetInformation'
import SeeInformation from '../views/SeeInformation'
import ManageUsers from '../views/ManageUsers'
import ChatInterface from '../views/ChatInterface'
import ManageRoles from '../views/ManageRoles'
import RoleInformation from '../views/RoleInformation'
import ChangeRole from '../views/ChangeRole'
import ModifyRole from '../views/ModifyRole'
import CreateRoles from '../views/CreateRoles'
import OrdersInformation from '../views/OrdersInformation'
import Recharge from '../views/Recharge'
import SeeFeedBack from '../views/SeeFeedBack'
import CreateInnerRoles from '../views/CreateInnerRoles'
import cookie from '../cookie/cookie'

import Vue from 'vue'
import VueRouter from 'vue-router'
Vue.use(VueRouter) // VueRouter插件初始化

// 创建了一个路由对象
const router = new VueRouter({
  // routes 路由规则们
  // route  一条路由规则 { path: 路径, component: 组件 }
  // mode: 'history',
  routes: [
    { path: '/', redirect: '/login_system' },
    { path: '/login_system', component: Login },
    { path: '/login_system/register', component: Register },
    { path: '/login_system/retrieve_password', component: FindPsd },
    { path: '/setting', component: Setting },
    { path: '/changePassword', component: ChangePsd },
    { path: '/feedback', component: FeedBack },
    { path: '/setInformation', component: SetInformation },
    { path: '/seeInformation', component: SeeInformation },
    { path: '/manageUsers', component: ManageUsers },
    { path: '/chatInterface', component: ChatInterface },
    { path: '/ManageRoles', component: ManageRoles },
    { path: '/RoleInformation', component: RoleInformation },
    { path: '/ChangeRole', component: ChangeRole },
    { path: '/ModifyRole', component: ModifyRole },
    { path: '/createRoles', component: CreateRoles },
    { path: '/ordersInformation', component: OrdersInformation },
    { path: '/recharge', component: Recharge },
    { path: '/seeFeedBack', component: SeeFeedBack },
    { path: '/CreateInnerRoles', component: CreateInnerRoles },
  ]
})

/*
* beforeEach:从一个页面跳转到另外一个页面时触发
* to:要跳转的页面
* from:从哪个页面出来
* next:决定是否通过
*/
router.beforeEach((to, from, next) => {
  // 如果跳转的页面不存在，跳转到404页面
  const destinationPath = to.fullPath;
  const user_id = cookie.getCookie('user_id')
  const match = destinationPath.match(/\?user_id=(\d+)/);
  if (to.matched.length === 0) {
    next('/404')
  }
  if (destinationPath === "/login_system") {
    next()
  } else {
    if (!user_id) {
      if (destinationPath === "/login_system" || destinationPath === "/login_system/register" || destinationPath === "/login_system/retrieve_password") {
        next()
      } else {
        next('/login_system')
      }
    } else if (match && match[1]) {
      const userId = match[1];
      if (userId === user_id) {
        next()
      } else {
        next('/login_system')
      }
    } else {
      console.log('666');
    }

  }
})

export default router