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
      <div class="top">
        <img src="../assets/background.png" alt="" class="backgroundImg">
        <div class="logo">
        </div>
        <img :src="this.user_imgUrl" alt="" class="logo">
        <h4 class='nickname'>{{this.user_name}}</h4>
      </div>
      <div class="myCollect">
        <div class="collectText">
          <ul class='collectTextWord'>
            <li class='one'>我</li>
            <li class='two'>的</li>
            <li class='three'>收</li>
            <li class='four'>藏</li>
          </ul>
        </div>
        <div class="collectContent">
          <div class="item" v-for="(item, index) in role_list" :key="index" v-show='item.is_collect'>
            <span class='roleName' @click="roleInfo(item.role_id, item.is_built_in, item.head_portrait_id)">{{formatText(item.role_name)}}</span>
            <span class='collectStar' @click="cancelCollect(item.role_id)">&#x2605;</span>
          </div>
        </div>
      </div>
      <div class="roleManage">
        <div class="roleText">
          <ul class='roleTextWord'>
            <li class='one'>角</li>
            <li class='two'>色</li>
            <li class='three'>管</li>
            <li class='four'>理</li>
          </ul>
        </div>
        <div class="roleContent">
          <div class="item" v-for="(item, index) in role_list" :key="index" v-show='!item.is_collect'>
            <span class='roleName' @click="roleInfo(item.role_id, item.is_built_in, item.head_portrait_id)">{{formatText(item.role_name)}}</span>
            <span class='star' v-show='!item.is_built_in' @click='collectRole(item.role_id)'>&#x2605;</span>
            <span  class='delete'  v-show='!item.is_built_in' @click='open_and_deleteRole(item.role_id)'>x</span>
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
      role_list: [],
      user_id: this.$route.query.user_id,
      delete_role_id: '',
      user_name: '',
      user_imgUrl: ''
    }

  },

  created () {
    document.title = '管理角色-chataaa'
    this.getInfo()
  },

methods: {

  async getInfo() {
    const res1 = await axios.get('http://8.134.178.190:5000/vip_user/get_roles', {
        params: {
          user_id: this.user_id
        }
      })
      if (res1.data.code === '400' ) {
      this.$message.error('获取角色失败！');
      return
        }
      // console.log(res1)
      this.role_list = res1.data.data
      this.user_name = res1.data.nickname
      const head_portrait_id = res1.data.head_portrait_id
      const res2 = await axios.get('http://8.134.178.190:5000//vip_user/get_role_head_portrait', {
        params: {
          head_portrait_id: head_portrait_id,
        },
        responseType: 'blob'
      })
      if (res1.data.code === '400' ) {
      this.$message.error('获取头像失败！');
      return
        }
      this.user_imgUrl = URL.createObjectURL(res2.data)
      // console.log(this.role_list);

  },
  async roleInfo(roleId, isBuild, headId) {
    this.$router.push({
        path: '/RoleInformation',
        query: {
              user_id: this.user_id,
              role_id: roleId,
              is_built_in: isBuild,
              head_portrait_id: headId,
            }
      })
    
  },

  formatText(text) {
    if (text.length > 5) {
    return `${text.slice(0, 5)}...`;
    }
    return text;
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

   async collectRole(roleId) {
     const res = await axios.post('http://8.134.178.190:5000//vip_user/collect_role', {
        role_id: roleId,
      })
      if (res.data.code === '400' ) {
      this.$message.error('收藏角色失败！');
      return
        }
     console.log(res)
     this.getInfo()
    },

    open_and_deleteRole(roleId) {
      this.delete_role_id = roleId
      this.open()
    },
    open() {
      this.$confirm('此操作将永久删除该角色, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.$message({
            type: 'success',
            message: '删除成功!'
          });
          this.deleteRole(this.delete_role_id)
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消删除'
          });          
        });

    },

    async deleteRole(roleId) {
      // console.log(roleId);
     const res = await axios.post('http://8.134.178.190:5000//vip_user/delete_user_role', {
        role_id: roleId,
      })
      if (res.data.code === '400' || res.data.code === '401') {
      this.$message.error('删除角色失败！');
      return
        }
     this.delete_role_id = ''
    //  console.log(res)
     this.getInfo()
    },

    async cancelCollect(roleId) {
     const res = await axios.post('http://8.134.178.190:5000//vip_user/cancel_collect', {
        role_id: roleId,
      })
       if (res.data.code === '400') {
      this.$message.error('取消收藏角色失败！');
      return
        }
    //  console.log(res)
     this.getInfo()
    },
    
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

  .top {
    position: relative;
    width: 1229px;
    height: 185px;
    background-color: skyblue;
    border-radius: 10px;
    margin-top: 14px;
    margin-left: 86px;
  }

  .top .backgroundImg {
    border-radius: 10px;
    width: 1229px;
    height: 185px;
  }

  .top .logo {
    width: 70px;
    height: 70px;
    position: absolute;
    /* background-color: black; */
    border-radius: 50%;
    /* border: 1px solid #000; */
    top: 100px;
    left: 5px
  }

  .top .nickname {
    position: absolute;
    color: white;
    top: 115px;
    left: 80px
  }

  .myCollect {
    display: flex;
    width: 1229px;
    height: 170px;
    /* background-color: yellow; */
    margin-top: 35px;
    margin-left: 86px;
  }

  .myCollect .collectText {
    border: 2px solid #bbbbbb;
    width: 122px;
    height: 100%;
    border-radius: 10px;
    background-color: #f2f5f8;
  }

  .myCollect .collectContent {
    border: 2px solid #bbbbbb;
    width: 1107px;
    border-radius: 10px;
    height: 100%;
    background-color: #f6fbff;
  }

  .collectTextWord {
    position: relative;
    color:black;
    font-weight: 400;
    font-size: 18px;
    text-align: center;
  }

  .collectTextWord .one {
    position: absolute;
    top: 20px;
    left: 50px;
  }

  .collectTextWord .two {
    position: absolute;
    top: 50px;
    left: 50px;
  }

.collectTextWord .three {
    position: absolute;
    top: 80px;
    left: 50px;
  }

  .collectTextWord .four {
    position: absolute;
    top: 110px;
    left: 50px;
  }

  .roleManage {
    display: flex;
    width: 1229px;
    height: 210px;
    /* background-color: black; */
    margin-top: 18px;
    margin-left: 86px;
  }

  .roleManage .roleText {
    border: 2px solid #bbbbbb;
    width: 122px;
    border-radius: 10px;
    height: 100%;
    background-color: #f2f5f8;
  }
  
  .roleTextWord {
    position: relative;
    color:black;
    font-weight: 400;
    font-size: 18px;
    text-align: center;
  }

  .roleTextWord .one {
    position: absolute;
    top: 30px;
    left: 50px;
  }

  .roleTextWord .two {
    position: absolute;
    top: 60px;
    left: 50px;
  }

.roleTextWord .three {
    position: absolute;
    top: 90px;
    left: 50px;
  }

  .roleTextWord .four {
    position: absolute;
    top: 120px;
    left: 50px;
  }

  .roleManage .roleContent {
    display: flex;
    flex-flow: row wrap;
    justify-content: flex-start;
    max-height: 210px;
    overflow-y: auto;
    border: 2px solid #bbbbbb;
    border-radius: 10px;
    width: 1107px;
    height: 100%;
    background-color: #f6fbff;
  }

   .item {
    position: relative;
    display: inline-block;
    border-radius: 10px;
    width: 130px;
    height: 42px;
    background-color: #c8e9fb;
    margin: 20px 30px 1px;
    border: 1px solid #ddd;
  }

  .item .roleName {
    position: absolute;
    line-height: 42px;
    font-weight: 500;
    color: #1a1c1d;
    left: 10px
  }

  .item .roleName:hover {
    color: #f6da06;
    cursor: pointer;
  }

  .item .star {
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    color: white;
    right: 23px;
    cursor: pointer;
  }

  .item .innerRoleStar{
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    color: white;
    right: 10px;
    cursor: pointer;
  } 

  .item .delete {
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    color: #838991;
    right: 9px;
    cursor: pointer;
  }

  .item .star:hover {
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    color: gold;
    right: 23px;
    cursor: pointer;
  }

.item .innerRoleStar:hover {
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    color: gold;
    right: 10px;
    cursor: pointer;
  }


  .item .delete:hover {
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    font-weight: 1000px;
    /* bottom: 1px; */
    color: #444a55;
    right: 9px;
    cursor: pointer;
  }

  .collectStar {
    position: absolute;
    line-height: 42px;
    font-size: 20px;
    color: gold;
    right: 10px;
    cursor: pointer;
  }
</style>