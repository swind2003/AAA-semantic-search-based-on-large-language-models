<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="setInfo()" class="one">信息设置</li>
        <li @click="manageUsers()" class="two">用户管理</li>
        <li @click="seeInfo()" class="three">查看信息</li>
        <li class="four active">用户反馈</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="middle">
      <div class="middleSetting">用户反馈</div>
      <div @click="see_no()" class="settingTop" :class="{'active':is_checked === 0}">未查看</div>
      <div @click="see_yes()" class="settingTop" :class="{'active':is_checked === 1}">已查看</div>
    </div>
    <div class="right">
      <div class="rightTop">查看反馈</div>
      <form v-show="!details">
        <div class="dateBegin">
          <select id="year" v-model="selectedYear1" @change="updateMonths1">
            <option v-for="year in availableYears1" :key="year" :value="year">{{ year }}</option>
          </select>
          <label for="year"> 年 </label>

          <select id="month" v-model="selectedMonth1" @change="updateDays1">
            <option v-for="month in availableMonths1" :key="month" :value="month">{{ month }}</option>
          </select>
          <label for="month"> 月 </label>

          <select id="day" v-model="selectedDay1">
            <option v-for="day in availableDays1" :key="day" :value="day">{{ day }}</option>
          </select>
          <label for="day"> 日 </label>
        </div>
        <div class="transition">————</div>
        <div class="dateEnd">
          <select id="year" v-model="selectedYear2" @change="updateMonths2">
            <option v-for="year in availableYears2" :key="year" :value="year">{{ year }}</option>
          </select>
          <label for="year"> 年 </label>

          <select id="month" v-model="selectedMonth2" @change="updateDays2">
            <option v-for="month in availableMonths2" :key="month" :value="month">{{ month }}</option>
          </select>
          <label for="month"> 月 </label>

          <select id="day" v-model="selectedDay2">
            <option v-for="day in availableDays2" :key="day" :value="day">{{ day }}</option>
          </select>
          <label for="day"> 日 </label>
        </div>
        <button @click="query()" class="query">查询</button>
        <button @click="showAll()" class="showAll">显示全部</button>
        <div class="Table">
          <table>
            <thead>
              <tr>
                <th style="width: 260px;">邮箱</th>
                <th style="width: 310px;">用户名</th>
                <th style="width: 170px;">日期</th>
                <th style="width: 160px;">查看</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in feed_list" :key="index">
                <td>{{ item.mail_account }}</td>
                <td>{{ item.nickname }}</td>
                <td>{{ item.date }}</td>
                <td><button @click="seeDetails(index)">查看详情</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </form>
      <form v-show="details">
        <div @click="back()" class="iconfont icon-chexiao"></div>
        <div class="source">
        <span>来自&nbsp; {{ mail_account }} &nbsp;的反馈</span>
        </div>
        <textarea v-model="feedback" cols="30" rows="10" disabled></textarea>
        <button @click="changeChess(index)" class="isChess">{{ showIsChess }}</button>
        <button @click="previous()" class="previous">&lt;</button>
        <button @click="next()" class="next">&gt;</button>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'SeeFeedBack',
  data () {
    return {
      user_id: this.$route.query.user_id,
      
      selectedYear1: '', // 开始选择年份
      selectedMonth1: '', // 开始选择月份
      selectedDay1: '', // 开始选择天数
      availableYears1: [],   // 存储可选的年份（开始）
      availableMonths1: [],  // 存储可选的月份（开始）
      availableDays1: [],   // 存储可选的天数（开始）

      selectedYear2: '', // 结束选择年份
      selectedMonth2: '', // 结束选择月份
      selectedDay2: '', // 结束选择天数
      availableYears2: [],   // 存储可选的年份（结束）
      availableMonths2: [],  // 存储可选的月份（结束）
      availableDays2: [],   // 存储可选的天数（结束）

      feed_list: [], // 反馈信息列表
      index: 0, // 反馈信息列表索引

      mail_account: '',
      feedback: '  反馈反馈反馈反馈反馈反馈反馈反馈反馈反馈反馈反馈反馈反馈',
      isChess: false, // true表示已确认，false表示未确认
      details: false, // false表示显示表格，否则显示详细反馈信息
      is_checked: 0, // 0表示未查看
      showIsChess: '未查看',
    }
  },

  created () {
    document.title = '查看反馈-chataaa'
    this.getInfo()
  },

  mounted() {
    this.updateYears1(); // 初始化开始年份
    this.updateMonths1(); // 初始开始化月份
    this.updateDays1(); // 初始化开始天数
    this.updateYears2(); // 初始化结束年份
    this.updateMonths2(); // 初始化结束月份
    this.updateDays2(); // 初始化结束天数
  },

  methods: {
    async getInfo () {
      const res = await axios.get('http://8.134.178.190:5000/administrator/check_feedback', {
        params: {
          is_checked: this.is_checked
        }
      })
      if (res.data.code === '400') {
        alert('获取信息错误')
        return
      }
      this.feed_list = res.data.data
    },
    see_no () {
      this.is_checked = 0
      this.getInfo()
      this.details = false
    },
    see_yes () {
      this.is_checked = 1
      this.getInfo()
      this.details = false
    },
    updateYears1() {
      const currentYear = new Date().getFullYear();
      // 如果当前年份不在availableYears中，则添加
      for (let Year = 2023; Year <= currentYear; Year++) {
        this.availableYears1.push(Year)
      }
    },
    updateMonths1() {
      const months = Array.from({ length: 12 }, (_, index) => index + 1);
      this.availableMonths1 = months;
      this.selectedMonth1 = ''; // 重置月份
      this.updateDays1(); // 更新天数
    },
    updateDays1() {
      const selectedYear = parseInt(this.selectedYear1);
      const selectedMonth = parseInt(this.selectedMonth1);
      const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
      const days = Array.from({ length: daysInMonth }, (_, index) => index + 1);
      this.availableDays1 = days;

      // 如果当前选择的天数超过新的天数范围，则重置为最大天数
      if (parseInt(this.selectedDay1) > daysInMonth) {
      this.selectedDay1 = '';
      }
    },
    updateYears2() {
      const currentYear = new Date().getFullYear();
      // 如果当前年份不在availableYears中，则添加
      for (let Year = 2023; Year <= currentYear; Year++) {
        this.availableYears2.push(Year)
      }
    },
    updateMonths2() {
      const months = Array.from({ length: 12 }, (_, index) => index + 1);
      this.availableMonths2 = months;
      this.selectedMonth2 = ''; // 重置月份
      this.updateDays2(); // 更新天数
    },
    updateDays2() {
      const selectedYear = parseInt(this.selectedYear2);
      const selectedMonth = parseInt(this.selectedMonth2);
      const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
      const days = Array.from({ length: daysInMonth }, (_, index) => index + 1);
      this.availableDays2 = days;

      // 如果当前选择的天数超过新的天数范围，则重置为最大天数
      if (parseInt(this.selectedDay2) > daysInMonth) {
      this.selectedDay2 = '';
      }
    },
    formatDate (year, month, day) {
      const formatMonth = String(month).padStart(2, '0')
      const formatDay = String(day).padStart(2, '0')
      return `${year}-${formatMonth}-${formatDay}`
    },
    async query () {
      if (this.selectedYear1 > this.selectedYear2 && this.selectedYear1 !== '' && this.selectedYear2 !== '') {
        alert('请输入正确的时间区间！')
        return
      } else if (this.selectedYear1 === this.selectedYear2 && this.selectedMonth1 > this.selectedMonth2) {
        alert('请输入正确的时间区间！')
        return
      } else if (this.selectedYear1 === this.selectedYear2 && this.selectedMonth1 === this.selectedMonth2 && this.selectedDay1 > this.selectedDay2) {
        alert('请输入正确的时间区间！')
        return
      } else if (this.selectedYear1 !== '' && this.selectedMonth1 !== '' && this.selectedDay1 !== '' && this.selectedYear2 !== '' && this.selectedMonth2 !== '' && this.selectedDay2 !== '') {
        const startDate = this.formatDate(this.selectedYear1, this.selectedMonth1, this.selectedDay1)
        const endDate = this.formatDate(this.selectedYear2, this.selectedMonth2, this.selectedDay2)
        const res = await axios.get('http://8.134.178.190:5000/administrator/check_feedback',{
          params: {
            is_checked: this.is_checked,
            start_date: startDate,
            end_date: endDate
          }
        })
        if (res.data.code === '400') {
          alert('获取信息错误')
          return
        }
        this.feed_list = res.data.data
      } else if (this.selectedYear1 === '' && this.selectedMonth1 === '' && this.selectedDay1 === '' && this.selectedYear2 !== '' && this.selectedMonth2 !== '' && this.selectedDay2 !== '') {
        const endDate = this.formatDate(this.selectedYear2, this.selectedMonth2, this.selectedDay2)
        const res = await axios.get('http://8.134.178.190:5000/administrator/check_feedback',{
          params: {
            is_checked: this.is_checked,
            end_date: endDate
          }
        })
        if (res.data.code === '400') {
          alert('获取信息错误')
          return
        }
        this.feed_list = res.data.data
      } else if (this.selectedYear1 !== '' && this.selectedMonth1 !== '' && this.selectedDay1 !== '' && this.selectedYear2 === '' && this.selectedMonth2 === '' && this.selectedDay2 === '') {
        const startDate = this.formatDate(this.selectedYear1, this.selectedMonth1, this.selectedDay1)
        const res = await axios.get('http://8.134.178.190:5000/administrator/check_feedback',{
          params: {
            is_checked: this.is_checked,
            start_date: startDate,
          }
        })
        if (res.data.code === '400') {
          alert('获取信息错误')
          return
        }
        this.feed_list = res.data.data
      } else {
        alert('请输入正确的时间区间！')
        return
      }
    },
    showAll () {
      this.getInfo()
      this.selectedYear1 = ''
      this.selectedYear2 = ''
      this.selectedMonth1 = ''
      this.selectedMonth2 = ''
      this.selectedDay1 = ''
      this.selectedDay2 = ''
    },
    seeDetails (index) {
      this.details = true
      this.index = index
      this.feedback = this.feed_list[index].content
      this.mail_account = this.feed_list[index].mail_account
      if (this.feed_list[index].is_checked === true) {
        this.showIsChess = '已查看'
      } else {
        this.showIsChess = '未查看'
      }
    },
    back () {
      this.details = false
      this.getInfo()
    },
    async changeChess (index) {
      if (this.feed_list[index].is_checked === false) {
        const res = await axios.post('http://8.134.178.190:5000/administrator/set_checked', {
          feedback_id: this.feed_list[index].feedback_id
        })
        if (res.data.code === '400') {
          alert('操作失败')
          return
        }
        this.feed_list[index].is_checked = true
        this.showIsChess = '已查看'
      } else {
        const res = await axios.post('http://8.134.178.190:5000/administrator/set_checked', {
          feedback_id: this.feed_list[index].feedback_id
        })
        if (res.data.code === '400') {
          alert('操作失败')
          return
        }
        this.feed_list[index].is_checked = false
        this.showIsChess = '未查看'
      }
    },
    previous () {
      if (this.index === 0) {
        alert('前面已经没有啦！')
      } else {
        this.index = this.index - 1
        this.mail_account = this.feed_list[this.index].mail_account
        this.feedback = this.feed_list[this.index].content
        if (this.feed_list[this.index].is_checked === false) {
          this.showIsChess = '未查看'
        } else {
          this.showIsChess = '已查看'
        }
      }
    },
    next () {
      if (this.index === this.feed_list.length - 1) {
        alert('已经是最后一个啦！')
      } else {
        this.index = this.index + 1
        this.mail_account = this.feed_list[this.index].mail_account
        this.feedback = this.feed_list[this.index].content
        if (this.feed_list[this.index].is_checked === false) {
          this.showIsChess = '未查看'
        } else {
          this.showIsChess = '已查看'
        }
      }
    },
    setInfo () {
      this.$router.push({
        path: '/setInformation',
        query: {
          user_id: this.user_id
        }
      })
    },
    manageUsers () {
      this.$router.push({
        path: '/manageUsers',
        query: {
          user_id: this.user_id
        }
      })
    },
    seeInfo () {
      this.$router.push({
        path: '/seeInformation',
        query: {
          user_id: this.user_id
        }
      })
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
  },
  
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
    background-color: #465069;
    opacity: 0.9;
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
    color: #1990FF;
  }

  .leftText .five {
    position: absolute;
    top: 570px;
  }

  .middle {
    position: relative;
    width: 200px;
    background-color: #F6FBFF;
    border: 1px solid #BBBBBB;
    font-size: 17px;
  }

  .middleSetting {
    padding: 5px 0 10px 20px;
    font-size: 20px;
  }

  .settingTop {
    text-align: center;
    padding-bottom: 12px;
  }

  .settingTop:hover {
    color: #1990FF;
    font-weight: 700;
    cursor: pointer;
  }

  .active {
    color: #1990FF;
    font-weight: 700;
  }

  .right {
    position: relative;
    width: 1250px;
    background-color: #F2F5F8;
  }

  .right .rightTop {
    font-size: 20px;
    font-weight: 700;
    height: 60px;
    text-align: center;
    line-height: 60px;
    margin: 0 auto;
    border-bottom: 1px solid #BBBBBB;
  }

  .right select,option {
    height: 25px;
  }

  .right .dateBegin {
    position: absolute;
    top: 100px;
    left: 220px;
    font-size: 17px;
  }

  .right .transition {
    position: absolute;
    top: 101px;
    left: 435px;
    font-weight: 700;
  }

  .right .dateEnd {
    position: absolute;
    top: 100px;
    left: 520px;
    font-size: 17px;
  }

  .right .query {
    position: absolute;
    top: 100px;
    left: 750px;
    font-size: 17px;
    width: 100px;
    height: 26px;
    background-color: #809CFF;
    border: none;
  }

  .right .query:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .showAll {
    position: absolute;
    top: 100px;
    left: 890px;
    font-size: 17px;
    width: 100px;
    height: 26px;
    background-color: #809CFF;
    border: none;
  }

  .right .showAll:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .Table {
    position: absolute;
    top: 150px;
    left: 175px;
    width: 900px;
    height: 550px;
    background-color: #fff;
    border: 2px solid #BBBBBB;
    overflow: auto;
  }

  table {
    border-collapse: collapse;
  }

  table th, td {
    text-align: center;
    width: 60px;
    height: 40px;
    border: 1px solid #BBBBBB;
  }

  td button {
    width: 90px;
    height: 25px;
    background-color: #9CBFFB;
    color: white;
    font-weight: 700;
    border-radius: 15px;
    border: none;
    cursor: pointer;
  }

  td button:hover {
    width: 92px;
    height: 27px;
    opacity: 0.7;
    transition: 0.5s;
  }

  .right .source {
    position: absolute;
    top: 110px;
    left: 30px;
    font-size: 17px;
  }

  .icon-chexiao {
    position: absolute;
    left: 10px;
    font-size: 30px;
    width: 30px;
    height: 30px;
    cursor: pointer;
  }

  textarea {
    position: absolute;
    top: 150px;
    left: 160px;
    font-size: 16px;
    width: 900px;
    height: 500px;
    background-color: #F6FBFF;
    outline: none;
    resize: none;
    border-radius: 15px;
    padding: 10px;
  }

  .isChess {
    position: absolute;
    top: 90px;
    right: 50px;
    width: 100px;
    height: 50px;
    font-size: 17px;
    font-weight: 700;
    background-color: #94cbff;
    border-radius: 10px;
    border: none;
    cursor: pointer;
  }

  .isChess:hover {
    width: 105px;
    height: 55px;
    opacity: 0.7;
    transition: 0.3s;
  }

  .previous {
    position: absolute;
    right: 170px;
    bottom: 29px;
    font-weight: 700;
    font-size: 25px;
    width: 70px;
    height: 40px;
    background-color: #94CBFF;
    border-radius: 10px;
    cursor: pointer;
  }

  .next {
    position: absolute;
    right: 90px;
    bottom: 29px;
    font-weight: 700;
    font-size: 25px;
    width: 70px;
    height: 40px;
    background-color: #94CBFF;
    border-radius: 10px;
    cursor: pointer;
  }

  .previous:hover {
    width: 72px;
    height: 42px;
    opacity: 0.7;
    transition: 0.5s;
  }

  .next:hover {
    width: 72px;
    height: 42px;
    opacity: 0.7;
    transition: 0.5s;
  }
</style>