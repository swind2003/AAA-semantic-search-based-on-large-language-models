import Vue from 'vue'
import App from './App.vue'
import router from './router/index'
import ElementUI from 'element-ui';
import 'element-ui/lib/theme-chalk/index.css';
import './css/base.css'
import '../iconfont/iconfont.css'
// import store from './store/store'
import axios from 'axios'
import cookie from './cookie/cookie'

Vue.use(ElementUI);
Vue.config.productionTip = false
axios.defaults.withCredentials = true
Vue.prototype.cookie = cookie
axios.defaults.baseURL = 'http://8.134.178.190:5000'

new Vue({
  render: h => h(App),
  router,
  // store
}).$mount('#app')
