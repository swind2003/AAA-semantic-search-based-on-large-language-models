<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li class="one">聊天框</li>
        <li @click="manageRoles()" class="two">角色管理</li>
        <li @click="createRoles()" class="three">新建角色</li>
        <li @click="setting()" class="four">设置</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleTop">
        <button @click="clickNewGroup()" class="newGroup">+ New Group</button> <button @click="clickNewChat()" class="newChat">+ New Chat</button>
      </div>
      <ul v-for="(group,index) in groups" :key="group.group_id" class="middleMain" :class="{middleMainMarginTop: index == 0}">
        <li @click="chooseGroup(group.group_id)" class="groupName" :class="{groupBorder: group.group_id === group_id}">
          <div class="name">
            <span v-show="group.change_group_name1 === 'true'" class="group_window__name">{{ group.group_name }}</span>
            <!-- <input v-model="group.group_name" type="text" disabled v-show="group.change_group_name1 === 'true'"> -->
            <input v-model="newGroupName" class="getBorder" type="text" name="" id="" v-show="group.change_group_name2 === 'true'">
            <div @click="chessRenameG()" class="yes" v-show="group.change_group_name2 === 'true'">√</div>
            <div @click="noRenameG(groups, index)" class="no" v-show="group.change_group_name2 === 'true'">×</div>
            <!-- <div>{{ group.group_name }}</div> -->
            <div @click="showWindows(groups, index)" class="iconfont icon-xiangxia" v-show="group.judge === 'true'"></div>
            <div @click="showWindows(groups, index)" class="iconfont icon-icon_on_the_top" v-show="group.judge === 'false'"></div>
          </div>
          <div class="icon">
            <div @click="changeGroupName(groups, index, group.group_name)" class="iconfont icon-bianxie"></div>
            <div @click="isDelG(group.group_id)" class="iconfont icon-shanchu"></div>
          </div>
        </li>
        <!-- <ul> -->
          <li @click="displayWindow(window.group_id, window.chat_window_id)" v-for="(window, index) in windows" :key="window.chat_window_id" class="chatName" v-show="group.group_id === window.group_id && group.judge === 'true'" :class="{chatBorder: window.chat_window_id === chat_window_id}">
            <div class="name">
              <div class="iconfont icon-duihua"></div>
              <span v-show="window.change_window_name1 === 'true'" class="group_window__name">{{ window.chat_window_name }}</span>
              <!-- <input v-model="window.chat_window_name" type="text" disabled v-show="window.change_window_name1 === 'true'"> -->
              <input v-model="newWindowName" class="getBorder" type="text" name="" id="" v-show="window.change_window_name2 === 'true'">
              <div @click="chessRenameW()" class="yes" v-show="window.change_window_name2 === 'true'">√</div>
              <div @click="noRenameW(windows, index)" class="no" v-show="window.change_window_name2 === 'true'">×</div>
            </div>
            <div class="icon">
              <div @click="changeWindowName(windows, index, window.chat_window_name)" class="iconfont icon-bianxie"></div>
              <div @click="changeG(windows, index)" class="iconfont icon-zhuanyi"></div>
              <div @click="isDelW(window.chat_window_id)" class="iconfont icon-shanchu"></div>
            </div>
          </li>
        <!-- </ul> -->
      </ul>
    </div>
    <div class="right">
      <div class="rightTop">
        <span>聊天角色选择:</span>
        <select v-model="flag" name="" id="">
          <option v-for="item in role_list" :key="item.role_id" :value="item.flag">{{ item.role_name }}</option>
        </select>
      </div>
      <div class="rightMiddle" ref="myDiv">
        <div class="container">
          <div class="message" v-for="(message,index) in messages" :key="index">{{ message.content }}</div>
        </div>
      </div>
      <div class="contactUsShow" v-show="isShowContact">
        <div @click="closeContact()" class="close">❎</div>
        <div class="contactTitle">联系我们</div>
        <div class="contactContent">{{ contactUs }}</div>
      </div>
      <div class="userMustKnowShow" v-show="isShowKnow">
        <div @click="closeMustKnow()" class="close">❎</div>
        <div class="userKnowtTitle">《用户须知》</div>
        <div class="userKnowContent">{{ userMustKnow }}</div>
      </div>
      <div class="times" v-show="chat_window_id !== ''">剩余次数：{{ times_remain }}/{{ times_all }}</div>
      <div class="loading" v-show="!isClickable">加载中...</div>
      <div class="rightBottom" v-show="chat_window_id !== ''">
        <textarea v-model="question" name="" id="" cols="30" rows="10" placeholder="点击输入"></textarea>
        <div @click="sendQuestion()" :class="{ 'disable': !isClickable }" class="iconfont icon-fasong"></div>
      </div>
      <div class="information">
        <div @click="contact()" class="contactUs">联系我们</div>
        <div @click="mustKnow()" class="userMustKnow">《用户须知》</div>
      </div>
      <div v-show="newGroup" class="overlay">
        <div class="setGroupName">
          <div>请输入分组名称</div>
          <input v-model="group_name" type="text">
          <br>
          <div class="chessCancel">
            <button @click="createGroup()">确定</button> <button @click="cancel()">取消</button>
          </div>
        </div>
      </div>
    </div>
    <!-- <a :href="link" target="_blank" class="advertisement">
      <img :src="advertisementPicture" alt="">
      <div @click="closeAdv()" class="closeAdv">❎</div></a> -->
    <div v-show="!advertise_state" class="advertisement">
      <a :href="link" target="_blank">
        <img :src="advertisementPicture" alt="">
      </a>
      <div @click="closeAdv()" class="closeAdv">❎</div>
    </div>
    <div v-show="changeGroup">
      <div class="changeTop">请选择您要移动到的分组</div>
      <div @click="close()" class="close">❎</div>
      <div class="changeGroup">
        <div @click="chessChange(group.group_id)" v-for="(group) in groups" :key="group.group_id" class="group">{{ group.group_name }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ChatInterface',
  data () {
    return {
      llm_type: '0',
      user_id: this.$route.query.user_id,
      role_id: '1',
      flag: '', // 标识模型
      question: '',
      isClickable: true, // 是否处于可发送聊天状态
      groups: [], // 分组
      windows: [], // 窗口
      role_list: [], // 模型数组
      messages: [1], // 聊天消息
      newGroup:false, // 显示新建分组窗口命名
      group_name: '', // 新建分组名称
      group_id: '', // 当前选中分组的id号
      chat_window_id: '', // 当前选中的窗口的id号
      newGroupName: '', // 重命名的分组名
      newWindowName: '', // 重命名的窗口名
      changeGroup: false, // 是否显示转移分组列表
      times_all: 9, // 总共次数
      times_remain: 9, // 剩余次数
      timer: null, // 定时器检查整点
      contactUs: '12345678910@qq.com', //联系我们内容
      userMustKnow: '用户须知', // 用户须知内容
      isShowContact: false, // true展示联系我们内容
      isShowKnow: false, // true展示用户须知内容
      advertise_state: true, // false显示广告
      advertisementPicture: null, // 广告图片
      link: 'ttps://item.taobao.com/item.htm?spm=a21n57.1.0.0.a1e1523cXSiIwo&id=675229061216&ns=1&abbucket=15#detail', // 广告跳转链接
      is_limit: false, // true表示该用户目前处于被限制登录状态
      isVip: false // true为VIP
    }
  },

  created () {
    document.title = '聊天-chataaa'
    this.getInfo()
    this.getTimes()
  },

  mounted () {
    if (this.role_list.length > 0) {
      this.llm_type = this.role_list[0].role_id
    }
    this.timer = setInterval(this.checkOnTheHour, 1000) // 每秒检查一次是否到整点
  },
  beforeDestroy () {
    clearInterval(this.timer)
  },

  methods: {
    checkOnTheHour () {
      const now = new Date()
      if (now.getMinutes() === 0 && now.getSeconds() === 0) { // 整点
        this.getTimes()
      }
    },
    async getTimes () {
      const res = await axios.get('http://8.134.178.190:5000/user/get_query_times', {
        params: {
          user_id: this.user_id
        }
      })
      if (res.data.code === '400') {
         this.$message.error('获取提问次数失败');
        return
      }
      this.times_all = res.data.all_query_times
      this.times_remain = res.data.current_query_times
    },
    huadong () {
      this.$nextTick(() => {
      const myDiv = this.$refs.myDiv;
      myDiv.scrollTop = myDiv.scrollHeight;
      })
    },
    async getInfo () {
      const res1 = await axios.get('http://8.134.178.190:5000/user/chat/get_all_group', {
        params: {
          user_id: this.user_id
        }
      })
      // console.log(res1)
      this.groups = res1.data.data

      const res2 = await axios.get('http://8.134.178.190:5000/user/chat/get_all_window', {
        params: {
          user_id: this.user_id
        }
      })
      // console.log(res2)
      this.windows = res2.data.data

      const res3 = await axios.get('http://8.134.178.190:5000/administrator/get_company_info')
      // console.log(res3)
      this.contactUs = res3.data.data.contact_way
      this.userMustKnow = res3.data.data.user_agreement

      const res4 = await axios.get('http://8.134.178.190:5000/user/get_advertising', {
        params: {

        },
        responseType: 'blob'
      })
      if (res4.data.code === '400') {
        this.$message.error('获取图片失败');
        return
      }
      const imgUrl = URL.createObjectURL(res4.data)
      this.advertisementPicture = imgUrl

      const res5 = await axios.get('http://8.134.178.190:5000/user/chat/get_all_role', {
        params: {
          user_id: this.user_id
        }
      })
      this.role_list = res5.data.data
      // console.log(this.role_list[0].role_id)
      this.flag = this.role_list[0].flag
      this.role_id = this.role_list[0].role_id
      this.llm_type = this.role_list[0].llm_type
      // console.log(res5)

      const res6 = await axios.get('http://8.134.178.190:5000/user/get_advertise_state', {
        params: {
          user_id: this.user_id
        }
      })
      if (res6.data.code === '400') {
        this.$message.error('获取广告状态失败');
        return
      }
      this.advertise_state = res6.data.advertise_state

      const res7 = await axios.get('http://8.134.178.190:5000/administrator/get_url_link')
      if (res7.data.code === '400') {
        this.$message.error('获取链接错误');
        return
      }
      this.link = res7.data.data.url

      const res8 = await axios.get('http://8.134.178.190:5000/user/get_vip_state', {
        params: {
          user_id: this.user_id
        }
      })
      if (res8.data.code === '400') {
        this.$message.error('获取vip身份失败');
        alert('获取vip身份失败')
        return
      }
      this.isVip = res8.data.state

      const res9 = await axios.get('http://8.134.178.190:5000/user/is_limit_login', {
        params: {
          user_id: this.user_id
        }
      })
      if (res9.data.code === '400') {
        alert('信息获取失败')
        return
      }
      this.is_limit = res9.data.is_limit
      if (this.is_limit === true) {
        alert('您已被限制登录')
        this.exit()
      }
    },
    contact () {
      this.isShowContact = true
    },
    closeContact () {
      this.isShowContact = false
    },
    mustKnow () {
      this.isShowKnow = true
    },
    closeMustKnow () {
      this.isShowKnow = false
    },
    async exit () {
      const res = await axios.post('http://8.134.178.190:5000/login_system/log_out', {
        user_id: this.user_id
      })
      if (res.data.code === '400') {
        this.$message.error('退出登录失败');
        return
      }
      this.cookie.clearCookie('remember_token')
      this.cookie.clearCookie('session')
      this.cookie.clearCookie('user_id')
      this.$router.push('/login_system')
    },
    showWindows (groups, index) {
      // this.isDown = !this.isDown
      // this.isUp = !this.isUp
      if (groups[index].judge === 'true') {
        groups[index].judge = 'false'
      } else {
        groups[index].judge = 'true'
      }
    },
    changeGroupName (groups, index, group_name) { // 点击分组重命名
      groups[index].change_group_name1 = 'false'
      groups[index].change_group_name2 = 'true'
      this.newGroupName = group_name
    },
    async chessRenameG () { // 重命名分组
      if (this.newGroupName === '') {
        alert(`名称不能为空`)
        return
      }
      const res = await axios.post('http://8.134.178.190:5000/user/chat/rename_group', {
        group_id: this.group_id,
        group_name: this.newGroupName
      })
      this.newGroupName = ''
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      this.getInfo()
    },
    noRenameG (groups, index) { // 取消重命名分组
      groups[index].change_group_name1 = 'true'
      groups[index].change_group_name2 = 'false'
    },
    async delG(group_id) { // 删除分组
      const res = await axios.delete(`http://8.134.178.190:5000/user/chat/delete_group?group_id=${group_id}`)
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      this.group_id = ''
      this.getInfo()
    },
    isDelG (group_id) { // 确认是否删除分组
      const isConfirmed = window.confirm('删除分组后，该分组下所有窗口也会被删除，确定要删除该分组吗？')
      if (isConfirmed) {
        this.delG(group_id)
      } else {
        console.log('取消删除分组')
      }
    },
    changeWindowName (windows, index, chat_window_name) { // 点击窗口重命名
      windows[index].change_window_name1 = 'false'
      windows[index].change_window_name2 = 'true'
      this.newWindowName = chat_window_name
    },
    async chessRenameW () { // 重命名窗口
      if (this.newWindowName === '') {
        alert(`名称不能为空`)
        return
      }
      const res = await axios.post('http://8.134.178.190:5000/user/chat/rename_window', {
        chat_window_id: this.chat_window_id,
        chat_window_name: this.newWindowName
      })
      this.newWindowName = ''
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      this.getInfo()
    },
    noRenameW (windows, index) { // 取消重命名窗口
      windows[index].change_window_name1 = 'true'
      windows[index].change_window_name2 = 'false'
    },
    changeG (windows, index) { // 显示转移窗口的分组列表
      if (this.changeGroup === true) {
        this.changeGroup = false
        return
      }
      this.chat_window_id = windows[index].chat_window_id
      this.changeGroup = true
    },
    async chessChange (group_id) { // 确实转移
      const res = await axios.post('http://8.134.178.190:5000/user/chat/group_add_window', {
        chat_window_id: this.chat_window_id,
        group_id: group_id
      })
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      this.getInfo()
      this.group_id = group_id
      this.displayWindow(group_id, this.chat_window_id)
    },
    close () { // 关闭转移窗口的分组列表
      this.changeGroup = false
    },
    async delW(chat_window_id) { // 删除窗口
      const res = await axios.delete(`http://8.134.178.190:5000/user/chat/delete_window?chat_window_id=${chat_window_id}`)
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      this.getInfo()
    },
    isDelW (chat_window_id) { // 确认是否删除窗口
      const isConfirmed = window.confirm('确定要删除该窗口吗？')
      if (isConfirmed) {
        this.delW(chat_window_id)
      } else {
        console.log('取消删除窗口')
      }
    },
    async displayWindow (group_id, chat_window_id) { // 点击窗口显示对应聊天页面及其聊天记录
      const res = await axios.get('http://8.134.178.190:5000/user/chat/get_recorder', {
        params: {
          chat_window_id: chat_window_id
        }
      })
      this.group_id = group_id
      this.chat_window_id = chat_window_id
      this.messages = res.data.data
      this.huadong()
    },
    clickNewGroup () { // 点击新建分组
      this.newGroup = true
    },
    async createGroup () { // 确定新建分组
      if (this.group_name === '') {
        alert('分组名称不能为空！')
        return
      }
      const res = await axios.post('http://8.134.178.190:5000/user/chat/new_group', {
        user_id: this.user_id,
        group_name: this.group_name
      })
      this.newGroup = false
      if (res.data.code === '400') {
        alert('操作失败')
        return
      }
      console.log(res)
      console.log(res.data.group_id)
      this.group_id = res.data.group_id
      this.getInfo()
      this.group_name = ''
      this.displayWindow(this.group_id, this.chat_window_id)
    },
    cancel () { // 取消新建分组
      this.newGroup = false
    },
    async clickNewChat () { // 新建窗口
      if (this.group_id === '') {
        alert(`请选中分组后再创建窗口`)
        return
      }
      const res = await axios.post('http://8.134.178.190:5000/user/chat/new_chat', {
        user_id: this.user_id,
        group_id: this.group_id
      })
      if (res.data.code === '401') {
        alert(`参数有误`)
      }
      if (res.data.code === '400') {
        alert(`创建失败，请重新创建`)
        return
      }
      console.log(res)
      console.log(res.data.chat_window_id)
      this.chat_window_id = res.data.chat_window_id
      this.getInfo()
      this.displayWindow(this.group_id, this.chat_window_id)
    },
    chooseGroup (group_id) { // 获取当前选中分组id号
      this.group_id = group_id
    },
    chooseWindow (group_id, chat_window_id) { // 获取当前选中窗口id号
      this.group_id = group_id
      this.chat_window_id = chat_window_id
    },
    async sendQuestion () { // 发送问题
      if (this.question.trim() === '') {
        alert(`输入内容不能为空`)
        return
      }
      this.isClickable = false
      const res = await axios.post('http://8.134.178.190:5000/semantic_search/query', {
        llm_type: this.llm_type,
        user_id: this.user_id,
        chat_window_id: this.chat_window_id,
        role_id: this.role_id,
        question: this.question
      })
      this.question = ''
      if (res.data.code === '400') {
        alert('提问失败')
        this.isClickable = true
        return
      }
      this.displayWindow(this.group_id ,this.chat_window_id)
      this.isClickable = true
      this.times_remain = res.data.current_query_times
      if (res.data.code === '403') {
        alert(`提问次数已达上限`)
        this.isClickable = true
        return
      }
      if (res.data.code === '400') {
        alert(`使用模型出现问题`)
        this.isClickable = true
        return
      }
    },
    closeAdv () {
      this.advertise_state = true
    },
    manageRoles() {
      if(this.isVip) {
        this.$router.push({
          path: '/ManageRoles',
          query: {
            user_id: this.user_id
          }
        })
      } else {
        alert('该功能为VIP用户专享，快去升级会员吧！')
      }
    },
    createRoles () {
      if (this.isVip) {
        this.$router.push({
          path: '/createRoles',
          query: {
            user_id: this.user_id
          }
        })
      } else {
        alert('该功能为VIP用户专享，快去升级会员吧！')
      }
    },
    setting () {
      this.$router.push({
        path: '/setting',
        query: {
          user_id: this.user_id
        }
      })
    }
  },

  watch: {
    flag(newVal) {
      const role = this.role_list.find(item => item.flag === newVal)
      if (role) {
        this.role_id = role.role_id
        this.llm_type = role.llm_type
      }
    }
  }
}
</script>

<style scoped>
  .wrapped {
    display: flex;
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: #f3f6f9;
    opacity: 0.9;
    flex-grow: 0;
  }

  .left {
    width: 90px;
    height: 100%;
    background-color: #D6ECFF;
    border-radius: 10px 0 0 10px;
  }

  .leftText {
    position: relative;
    color: #9CBFFB;
    font-weight: 700;
    font-size: 18px;
    text-align: center;
  }

  .leftText li {
    width: 90px;
    height: 50px;
    line-height: 50px;
    border: 2px solid #9CBFFB;
    border-radius: 10px;
  }

  .leftText li:hover {
    background-color: #a0bff5;
    color: #1990FF;
    cursor: pointer;
  }

  .leftText .one {
    position: absolute;
    top: 90px;
    color: #1990FF;
  }

  .leftText .two {
    position: absolute;
    top: 210px;
  }

  .leftText .three {
    position: absolute;
    top: 330px;
  }

  .leftText .four {
    position: absolute;
    top: 450px;
  }

  .leftText .five {
    position: absolute;
    top: 570px;
  }

  .middle {
    position: relative;
    width: 350px;
    background-color: #F6FBFF;
    border: 1px solid #BBBBBB;
    overflow: auto;
  }

  .middle .middleTop {
    position: fixed;
    width: 350px;
    height: 52px;
    padding: 10px;
    background-color: #F6FBFF;
    border: 1px solid #4095E5;
    font-size: 17px;
    z-index: 999;
  }

  .middleTop .newGroup {
    width: 100px;
    height: 35px;
    background-color: #F6FBFF;
    border: 1px solid #4095E5;
    border-radius: 5px;
    margin-left: 45px;
    margin-right: 30px;
  }

  .middleTop .newChat {
    width: 100px;
    height: 35px;
    background-color: #F6FBFF;
    border: 1px solid #4095E5;
    border-radius: 5px;
  }

  .middle .newGroup:hover {
    opacity: 0.7;
    cursor: pointer;
  }

  .middle .newChat:hover {
    opacity: 0.7;
    cursor: pointer;
  }

  .middleMain {
    /* margin-top: 60px; */  /* v-bind另起一个选择器
    第一个分组才有，其他分组不用加上外边距 */
    /* margin-top: 60px; */
    font-size: 15px;
  }

  .middleMainMarginTop {
    margin-top: 52px;
  }

  .middleMain .groupName {
    position: relative;
    display: flex;
    width: 348px;
    height: 40px;
    justify-content: center;
    cursor: pointer;
  }

  .middleMain .groupName:hover {
    border: 1px solid #4095E5;
  }

  .middleMain .groupBorder {
    border: 1px solid #4095E5;
  }

  .groupName .name {
    display: flex;
    padding-right: 30px;
    align-items: center;
  }

  .groupName .name div {
    cursor: pointer;
  }

  .groupName .icon {
    display: flex;
    position: absolute;
    top: 3px;
    right: 10px;
  }

  .groupName .icon-xiangxia, .icon-icon_on_the_top, .icon-bianxie{
    color: #000;
    font-size: 20px;
    padding-right: 10px;
    cursor: pointer;
  }

  .group_window__name {
    width: 200px;
    height: 20px;
    overflow: hidden;
  }

  .icon-shanchu {
    color: #000;
    font-size: 20px;
    padding-right: 10px;
    cursor: pointer;
  }

  .middleMain .chatName {
    position: relative;
    display: flex;
    width: 348px;
    height: 40px;
    justify-content: left;
    cursor: pointer;
  }

  .middleMain .chatName:hover {
    border: 1px solid #4095E5;
  }

  .middleMain .chatBorder {
    border: 1px solid #4095E5;
  }

  .chatName .name {
    display: flex;
    padding-left: 10px;
    align-items: center;
  }

  .chatName .icon {
    display: flex;
    position: absolute;
    top: 3px;
    right: 10px;
  }

  .chatName .icon-bianxie, .icon-zhuanyi, .icon-shanchu{
    color: #000;
    font-size: 20px;
    padding-right: 10px;
    cursor: pointer;
  }

  .middle input {
    width: 150px;
    height: 26px;
    border: none;
    padding: 5px;
    background-color: #F6FBFF;
    font-size: 16px;
    font-weight: 700;
    margin-right: 5px;
  }

  .middle .getBorder {
    border: 1px solid #000;
  }

  .name .yes {
    width: 26px;
    height: 26px;
    text-align: center;
    line-height: 26px;
    border: 1px solid #BBBBBB;
    cursor: pointer;
  }

  .name .no {
    width: 26px;
    height: 26px;
    text-align: center;
    line-height: 26px;
    border: 1px solid #BBBBBB;
    cursor: pointer;
  }

  .right {
    position: relative;
    width: 1000px;
    background-color: #F2F5F8;
  }

  .rightTop {
    position: relative;
    /* width: 1100px; */
    height: 50px;
    border-bottom: 1px solid #BBBBBB;
  }

  .rightTop span {
    position: absolute;
    left: 390px;
    top: 13px;
    font-size: 16px;
    font-weight: 700;
    /* color: #309bff; */
  }

  .rightTop select {
    position: absolute;
    width: 150px;
    height: 36px;
    left: 500px;
    top: 7px;
    background-color: skyblue;
    text-align: center;
    transition: background-color 0.3s ease;
    opacity: 0.7;
  }

  .rightTop select:hover {
    background-color: #D6ECFF;
    opacity: 1;
  }

  .right .rightMiddle {
    overflow: auto;
    position: absolute;
    width: 940px;
    height: 530px;
    left: 30px;
    top: 60px;
    background-color: #D6ECFF;
    border-radius: 10px;
    border: 1px solid #BBB;
  }

  .chat {
    width: 200px;
    height: 200px;
    background-color: #fff;
    border-radius: 10px;
  }

  .times {
    position: absolute;
    bottom: 70px;
    left: 60px;
    font-size: 17px;
    font-weight: 700;
    color: #309bff;
  }

  .loading {
    position: absolute;
    bottom: 70px;
    right: 1px;
    font-size: 17px;
    font-weight: 700;
  }

  .rightBottom {
    display: flex;
    position: absolute;
    left: 200px;
    bottom: 45px;
    align-items: center;
  }

  .rightBottom textarea {
    width: 700px;
    height: 70px;
    outline: none;
    resize: none;
    padding: 10px;
    font-size: 15px;
    border-radius: 10px;
  }

  .rightBottom .icon-fasong {
    font-size: 30px;
    /* margin-left: 10px; */
    cursor: pointer;
  }

  .right .information {
    display: flex;
    position: absolute;
    width: 400px;
    height: 30px;
    left: 480px;
    bottom: 5px;
    font-weight: 700;
    font-size: 14px;
  }

  .right .contactUs {
    margin-right: 40px;
  }

  .right .contactUs:hover {
    color: #1990FF;
    cursor: pointer;
  }

  .right .userMustKnow {
    margin-left: 20px;
  }

  .right .userMustKnow:hover {
    color: #1990FF;
    cursor: pointer;
  }

  .advertisement {
    position: absolute;
    width: 800px;
    height: 500px;
    left: 400px;
    top: 120px;
    z-index: 1005;
  }

  .advertisement img {
    width: 800px;
    height: 500px;
  }

  .advertisement .closeAdv {
    position: absolute;
    right: 10px;
    top: 10px;
    cursor: pointer;
  }

  .contactUsShow {
    position: relative;
    width: 500px;
    height: 200px;
    background-color: #F6FBFF;
    border: 3px solid #000;
    text-align: center;
    top: 200px;
    left: 260px;
    border-radius: 15px;
    z-index: 1120;
  }

  .contactUsShow .contactTitle {
    font-weight: 700;
    font-size: 20px;
    margin-top: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #BBBBBB;
  }

  .contactUsShow .contactContent {
    font-size: 25px;
    margin-top: 30px;
  }

  .contactUsShow .close {
    position: absolute;
    top: 2px;
    left: 460px;
    font-size: 20px;
  }

  .userMustKnowShow {
    position: relative;
    width: 700px;
    height: 300px;
    background-color: #F6FBFF;
    border: 3px solid #000;
    text-align: center;
    top: 150px;
    left: 200px;
    border-radius: 15px;
    z-index: 1120;
  }

  .userMustKnowShow .userKnowtTitle {
    font-weight: 700;
    font-size: 20px;
    margin-top: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #BBBBBB;
  }

  .userMustKnowShow .userKnowContent {
    overflow: auto;
    width: 700px;
    height: 240px;
    font-size: 16px;
    margin-top: 5px;
  }

  .userMustKnowShow .close {
    position: absolute;
    top: 2px;
    left: 660px;
    font-size: 20px;
  }

  .container {
    display: flex;
    flex-direction: column;
    z-index: 10;
  }

  .message {
    background-color: #f1f1f1;
    padding: 10px;
    margin: 5px;
    max-width: 70%;
    overflow-wrap: break-word;
    white-space: pre-wrap;
  }

  .message:nth-child(even) {
    align-self: flex-start;
  }

  .message:nth-child(odd) {
    align-self: flex-end;
  }

  .disable {
    pointer-events: none;
    opacity: 0.5;
  }

  .changeGroup {
    position: absolute;
    width: 220px;
    height: 600px;
    left: 436px;
    top: 50px;
    background-color: #F6FBFF;
    border: 1px solid #BBBBBB;
    border-radius: 0 0 10px 0;
    overflow: auto;
  }

  .changeTop {
    position: absolute;
    width: 220px;
    height: 50px;
    left: 436px;
    text-align: center;
    line-height: 50px;
    font-weight: 700;
    background-color: #F6FBFF;
    border-radius: 0 10px 0 0;
    border-right: 1px solid #BBBBBB;
    border-top: 1px solid #BBBBBB;
  }

  .close {
    position: absolute;
    left: 630px;
    top: 2px;
    cursor: pointer;
  }

  .changeGroup .group {
    width: 200px;
    height: 40px;
    border-bottom: 1px solid #BBB;
    text-align: center;
    line-height: 40px;
    margin: 0 auto;
  }

  .changeGroup .group:hover {
    border: 1px solid #1990FF;
    cursor: pointer;
  }

  .right .overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }

  .right .setGroupName {
    position: absolute;
    width: 300px;
    height: 120px;
    background-color: #F6FBFF;
    border: 3px solid #000;
    text-align: center;
    border-radius: 10px;
    top: 250px;
    left: 110px;
  }

  .setGroupName .chessCancel {
    position: absolute;
    width: 200px;
    height: 30px;
    left: 70px;
    bottom: 10px;
  }

  .setGroupName input {
    width: 240px;
    height: 30px;
    margin-top: 10px;
  }

  .chessCancel button {
    width: 40px;
    height: 25px;
    background-color: #fff;
    border-radius: 5px;
    margin-right: 40px;
  }

  .chessCancel button:hover {
    opacity: 0.6;
    cursor: pointer;
  }
</style>
