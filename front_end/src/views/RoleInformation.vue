<template>
  <div class="wrapped">
    <div class="left">
      <ul class="leftText">
        <li @click="toChat()" class="one">聊天框</li>
        <li class="two">角色管理</li>
        <li class="three" @click="toCreateRoles()">新建角色</li>
        <li class="four" @click="toSetting()">设置</li>
        <li class="five" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="right">
      <div class="box">
        <div class="top">
          <h2>角色信息</h2>
        </div>
        <div class="tbody">
          <div class="PictureAndName">
            <img :src="imgUrl" alt="">
            <h4>{{role_info.role_name}}</h4>
          </div>
          <h4 class='roledescription'>角色描述：{{role_info.description}}</h4>
          <div class="prompt">
            <h4>提示词prompt</h4>
            <div class="content">
              <span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{role_info.prompt ? role_info.prompt : '(当前角色没有提示词)'}}
                
                </span>
            </div>
          </div>
          <h4 class='ability'>发散能力：{{role_info.divergency}}</h4>
          <h4 class='model'>使用模型：{{role_info.module_name}}</h4>
          <div class="return" @click="backToManage()">
            <span >返 回</span>
          </div>
        </div>
      </div>
    </div>
  </div>  
</template>

<script>
import axios from 'axios'
export default {
  data () {
    return {
      role_info: '',
      user_id: this.$route.query.user_id,
      role_id: this.$route.query.role_id,
      is_built_in: this.$route.query.is_built_in,
      imgUrl: '',
      head_portrait_id: this.$route.query.head_portrait_id,
      is_limit: false, // true表示该用户目前处于被限制登录状态

    }
  },

  async created () {
    document.title = '角色信息-chataaa'
    this.getInfo()
    const res2 = await axios.get('http://8.134.178.190:5000/user/is_limit_login', {
        params: {
          user_id: this.user_id
        }
      })
      if (res2.data.code === '400') {
        alert('信息获取失败')
        return
      }
      this.is_limit = res2.data.is_limit
      if (this.is_limit === true) {
        alert('您已被限制登录')
        this.exit()
      }
  },

  methods: {
    backToManage() {
      this.$router.push({
        path: '/ManageRoles',
        query: {
              user_id: this.user_id,
            }
      })
    },

    toChat () {
      this.$router.push({
        path: '/chatInterface',
        query: {
          user_id: this.user_id
        }
      })
    },

  toCreateRoles() {
      this.$router.push({
        path: '/CreateRoles',
        query: {
              user_id: this.user_id,
            }
      })
  },

  toSetting() {
    this.$router.push({
        path: '/Setting',
        query: {
              user_id: this.user_id,
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

    async getInfo() {
      const res1 = await axios.get('http://8.134.178.190:5000//vip_user/get_role_information', {
        params: {
          role_id: this.role_id,
          is_built_in: this.is_built_in
        }
      })
      if (res1.data.code === '400') {
      this.$message.error('获取角色信息失败！');
      return
        }
      // console.log(res1)
      this.role_info = res1.data.data
      console.log(this.role_info);
       const res2 = await axios.get('http://8.134.178.190:5000//vip_user/get_role_head_portrait', {
        params: {
          head_portrait_id: this.head_portrait_id,
        },
        responseType: 'blob'
      })
      if (res2.data.code === '400') {
      this.$message.error('获取头像信息失败！');
      return
        }
      this.imgUrl = URL.createObjectURL(res2.data)
      console.log(this.imgUrl);
      // console.log(this.imgUrl);
    }

    
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
    background-color: #F2F5F8;
    opacity: 0.9;
  }

  .left {
    width: 90px;
    /* height: 705px; */
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
    color: #1990FF;
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

  .right {
    width: 1400px;
    background-color: #F2F5F8;
  }

  .box {
    width: 636px;
    height: 100%;
    background-color: #ffffff;
    border: 2px solid #787a7b;
    margin-left: 380px;
  }

  .box .top {
    height: 54px;
    width: 100%;
    background-color: #FFFFFF;
    margin-left: 0;
    margin-top: 0;
    border-radius: 0;
    border-bottom: 2px solid #cacaca;
  }

  .box .top h2 {
    text-align: center;
    line-height: 54px;
    color: #101010;
  }
  .PictureAndName {
    display: flex;
    width: 100%;
    height: 100px;
    background-color: #ffffff;
  }

  .tbody .roledescription {
    width: 100%;
    height: 78px;
    font-weight: 500;
    text-align: center;
    line-height: 30px;
    color: #2a2a2a;
    background-color: #ffffff
  }

  .PictureAndName img {
    width: 90px;
    height: 90px;
    margin-left: 90px;
    margin-top: 7px;
    border-radius: 50%;
  }

  /* .PictureAndName .name {
background-color: skyblue;
  } */

 .PictureAndName  h4 {
  display: inline-block;
  margin-left: 50px;
  margin-top: 35px;
 }

 .prompt {
  width: 545px;
  height: 184px;
  background-color: #ffffff;
  margin-left: 45px;
  border: 2px solid #b4c5ff;
  border-radius: 15px;
 }
 
  .prompt h4 {
    margin-top: 15px;
    margin-left: 5px;
  }

  .prompt .content {
    padding-left: 5px;
    width: 530px;
    height: 130px;
    overflow-y: auto;
    border: 1px solid #ccc;
  }

  .prompt .content span {
    font-size: 12px;
    color: #8491a4;
  }

  .tbody .ability {
    display: inline-block;
    margin-top: 40px;
    margin-left: 80px;
    margin-right: 130px;
  }

  .tbody .model {
    display: inline-block;
    /* margin-top: 40px; */
  }
  
  .tbody .return {
    height: 40px;
    width: 545px;
    background-color: #3182ce;
    margin-left: 45px;
    margin-top: 60px;
    padding-left: 260px;
    border-radius: 10px;
  }

  .tbody .return span {
    text-align: center;
    line-height: 40px;
    color: #fcfdfe;
  }

   .tbody .return:hover {
    opacity: 0.7;
    cursor: pointer;
  }
  
 
</style>