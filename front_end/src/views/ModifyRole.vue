<template>
  <div class="wrapped" v-loading="loading" element-loading-text="修改角色中" element-loading-spinner="el-icon-loading" element-loading-background="rgba(0, 0, 0, 0.8)">
    <div class="left">
      <ul class="leftText">
        <li class="one">修改角色</li>
        <li class="two" @click="toCreateInnerRoles()">新增角色</li>
        <li class="three" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="right">
      <div v-if="isModifying" class="modifying">
        <div class="title">修改角色</div>
        <div class="prompt">提示词</div>
        <textarea name="" id="" cols="30" rows="10" :placeholder="role_info.prompt ? role_info.prompt : '(当前角色没有提示词)'" v-model='prompt'></textarea>

        <input ref="pictureInput" type="file" style="display: none;" @change="handlePictureChange">
        <div class="head_text">角色头像：</div>
        <div v-show="!isModify" @click="triggerPictureInput()" class="head_picture">＋</div>
        <div v-show="isModify" @click="triggerPictureInput()" class="show_picture">
          <img :src="picture_show" alt="">
        </div>
        <div class="name">角色名称：</div>
        <!-- <input type="text" :placeholder="role_info.role_name" class="nameInput" v-model='role_name'> -->
        <el-input type="text" :placeholder="role_info.role_name" v-model="role_name" maxlength="25" show-word-limit class="nameInput"></el-input>
        <div class="describe">角色描述：</div>
        <!-- <input type="text" :placeholder="role_info.description" class="describeInput" v-model='description'> -->
        <el-input type="text" :placeholder="role_info.description" v-model="description" maxlength="25" show-word-limit class="describeInput"></el-input>
        <div class="divergence">发散能力：</div>
        <select name="" id="" class="divergenceSelect">
          <option selected disabled>1.0</option>
        </select>
        <div class="model">使用模型：</div>
        <select name="" id="" class="modelSelect">
          <option selected disabled>ChatGpt3.5</option>
        </select>
        <button class="modify" @click="open_and_saveChange()">保存</button>
        <button class="return" @click="returnDisplay()">返回</button>

        <div class="show_file">{{ file_show }}</div>
      </div>
      <div v-else class="display">
        <div class="title">角色详细信息</div>
        <div class="prompt">提示词</div>
        <!-- {{role_info.prompt ? role_info.prompt : '(当前角色没有提示词)'}} -->
        <!-- <textarea name="" id="" cols="30" rows="10" placeholder="    我想要让你作为一位杰出的律师。您将在法律领域展现您的才能，为人们提供准确、明晰的法律建议。您可以选择专攻领域，如刑法、民法、商法等，但您的目标是成为一位擅长处理各类法律问题、具备卓越法律洞察力的律师。"></textarea> -->
        <div class="tarea"><span>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{{role_info.prompt ? role_info.prompt : '(当前角色没有提示词)'}}</span></div>
        <input ref="pictureInput" type="file" style="display: none;" @change="handlePictureChange">
        <div class="head_text">角色头像：</div>
        <div class="show_picture">
          <img :src="imgUrl" alt="">
        </div>
        <div class="name">角色名称：<span>{{role_info.role_name}}</span></div>
        <div class="describe">角色描述：<span>{{role_info.description}}</span></div>

        <div class="divergence">发散能力：<span>1.0</span></div>
        <div class="model">使用模型：<span>ChatGpt3.5</span></div>
        <button class="save" @click="change()">修改</button>
        <button class="return" @click="returnChangeRole()">返回</button>

        <div class="show_file">{{ file_show }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ModifyRoles',
  data () {
    return {
      user_id: this.$route.query.user_id,
      role_id: this.$route.query.role_id,
      role_info: '',
      imgUrl: '',
      prompt: '',
      role_name: '',
      description: '',
      temp_imgUrl: '',
      temp_prompt: '',
      temp_role_name: '',
      temp_description: '',
      isModifying: false,
      isModify: false,
      picture_get: null, // 获取上传的头像图片
      picture_show: null, // 展示上传的头像图片
      file: null, // 上传的AI资料
      file_show: null,
      loading: false
    }
  },

  created () {
    document.title = '修改角色-chataaa'
    this.getInfo()
  },


  methods: {

    toCreateInnerRoles() {
      this.$router.push({
        path: '/CreateInnerRoles',
        query: {
              user_id: this.user_id,
            }
      })

    },

    returnChangeRole() {
      this.$router.push({
        path: '/ChangeRole',
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
      const res = await axios.get('http://8.134.178.190:5000///builtin_role_administrator/information/get_role_information_detail', {
        params: {
          user_id: "000000",
          role_id: this.role_id,
        }
      })
      if (res.data.code === '400' ) {
      this.$message.error('获取数据失败！');
    } 
      this.role_info = res.data
      // console.log(this.role_info);
      this.getPictures (this.role_id)
      this.getInputValue(this.role_info)
    },

    async getPictures (roleId) {
        const res = await axios.get('http://8.134.178.190:5000/builtin_role_administrator/information/get_role_head_portrait', {
          params: {
            role_id: roleId,
            user_id: "000000"
          },
          responseType: 'blob'
        })
        if (res.data.code === '400' ) {
      this.$message.error('获取头像失败！');
    } 
        this.imgUrl = URL.createObjectURL(res.data)
    },

    getInputValue (roleInfo) {
      this.prompt = roleInfo.prompt 
      this.role_name = roleInfo.role_name
      this.description = roleInfo.description 
    },


    triggerPictureInput () {
      this.$refs.pictureInput.click()
    },
    handlePictureChange (event) {
      const picture_temp = event.target.files[0]
      if (picture_temp && picture_temp.type.startsWith('image/')) {
        this.picture_get = picture_temp
        this.picture_show = URL.createObjectURL(this.picture_get)
        this.isModify = true
      } else {
        alert('请选择图片文件')
        event.target.value = null
      }
    },
    triggerFileInput () {
      this.$refs.fileInput.click()
    },
    handleFileChange (event) {
      this.file = event.target.files[0]
      this.file_show = this.file ? this.file.name : null
    },
    change () {
      this.isModifying = true;
      this.temp_imgUrl = this.imgUrl
      this.temp_prompt = this.prompt
      this.temp_role_name = this.role_name
      this.temp_description = this.description
    },

    open_and_saveChange() {
      this.open()
    },

    open() {
        this.$confirm('此操作将永久修改该内置角色, 是否继续?', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }).then(() => {
          this.saveChange()
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '已取消修改'
          });          
        });
      },

    async saveChange () {
      // console.log(this.picture_get);
      if (this.role_name.trim() === '') {
        this.$message({
          message: '请输入角色名称！',
          type: 'warning'
        });
        return
      } else if (this.description.trim() === '') {
        this.$message({
          message: '请输入角色描述！',
          type: 'warning'
        });
        return
      }
      this.isModify = false
      this.temp_imgUrl = this.imgUrl
      this.temp_prompt = this.prompt
      this.temp_role_name = this.role_name
      this.temp_description = this.description
      let file = new FormData()
      file.append('head_portrait', this.picture_get)
      file.append('user_id', "000000")
      file.append('role_id', this.role_id)
      file.append('role_name', this.role_name)
      file.append('description', this.description)
      file.append('prompt', this.prompt)
      this.loading = true
      const res = await axios.post('http://8.134.178.190:5000/builtin_role_administrator/edit_role_attribute', file
      // {
      //   headers: {
      //     'Content-Type': 'multipart/form-data',
      //   },
      // }
      )
      this.loading = false
      // console.log(res)
      if (res.data.code === '200') {
      this.$message({
          message: '修改成功！',
          type: 'success'
        });
    } else if (res.data.code === '400' || res.data.code === '401' || res.data.code === '402') {
      this.$message.error('修改失败！');
    } else if (res.data.code === '403') {
      this.$message.error('角色头像图片格式不符合要求！');
    }
      this.getInfo()
      this.file_show1 = this.file_show2
      this.isCloseShow = this.isClose
      this.isModifying = false
    },

    returnDisplay() {
      this.isModifying = false;
      this.isModify = false
      this.imgUrl = this.temp_imgUrl
      this.prompt = this.temp_prompt
      this.role_name = this.temp_role_name
      this.description = this.temp_description
      this.getInfo()

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
    background-color: #465069;
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
    color: #1990FF;
  }

  .leftText .two {
    position: absolute;
    top: 250px;
    color: #9CBFFB;
  }

  .leftText .three {
    position: absolute;
    top: 420px;
  }

   .right {
    position: relative;
    width: 1450px;
    background-color: #F2F5F8;
    /* background-image: url('../assets/createRoles.png'); */
    /* background-repeat: no-repeat; */
    background-size: 1450px 920px;
  }

  .right .modifying,.display {
    position: relative;
    width: 700px;
    height: 100%;
    background-color: #fff;
    border: 1px solid #BBB;
    margin: 0 auto;
  }



  .right .title {
    width: 700px;
    height: 40px;
    border-bottom: 1px solid #BBB;
    font-size: 17px;
    line-height: 40px;
    text-align: center;
    font-weight: 700;
  }

  .right .prompt {
    position: absolute;
    left: 70px;
    top: 50px;
    font-size: 17px;
    font-weight: 700;
    z-index: 99;
  }
  
  
  .right textarea {
    position: absolute;
    left: 60px;
    top: 75px;
    width: 580px;
    height: 200px;
    background-color: #fff;
    border: 1px solid #809CFF;
    border-radius: 15px;
    padding: 10px;
    font-size: 18px;
    resize: none;
  }

  .right .tarea {
    overflow-y: auto;
    position: absolute;
    left: 60px;
    top: 75px;
    width: 580px;
    height: 200px;
    background-color: #fff;
    border: 1px solid #809CFF;
    border-radius: 15px;
    padding: 10px;
    font-size: 18px;
    resize: none;
    /* padding-top: 35px; */
  }

  .right .head_text {
    position: relative;
    font-size: 17px;
    font-weight: 700;
    top: 280px;
    left: 60px;
  }

  .right .head_picture {
    position: absolute;
    top: 290px;
    left: 150px;
    width: 90px;
    height: 90px;
    background-color: #fff;
    border: 2px dashed #BBB;
    border-radius: 10px;
    color: #BBB;
    font-size: 40px;
    line-height: 75px;
    text-align: center;
  }

  .right .head_picture:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .name {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 410px;
  }
  
  .right .nameInput {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 400px;
    width: 500px;
    height: 27px;
    padding: 2px;
  }

  .right .describe {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 460px;
  }

  .right .describeInput {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 450px;
    width: 500px;
    height: 27px;
    padding: 2px;
  }

  .right .divergence {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 510px;
  }

  .right .divergenceSelect {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 510px;
    width: 120px;
    height: 27px;
    padding: 2px;
  }

  .right .model {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 560px;
  }

  .right .modelSelect {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 560px;
    width: 120px;
    height: 27px;
    padding: 2px;
  }

  .right .AI {
    position: absolute;
    font-size: 17px;
    font-weight: 700;
    left: 60px;
    top: 620px;
  }

  .right .AIupload {
    position: absolute;
    font-size: 16px;
    left: 150px;
    top: 610px;
    width: 100px;
    height: 40px;
    padding: 2px;
    background-color: #3182ce;
    color: #fff;
    border: none;
    border-radius: 10px;
  }

  .right .AIupload:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .modify {
    position: absolute;
    font-size: 17px;
    left: 100px;
    bottom: 20px;
    width: 200px;
    height: 40px;
    background-color: #3182ce;
    color: #fff;
    border: none;
    border-radius: 7px;
  }

  .right .return {
    position: absolute;
    font-size: 17px;
    left: 400px;
    bottom: 20px;
    width: 200px;
    height: 40px;
    background-color: #3182ce;
    color: #fff;
    border: none;
    border-radius: 7px;
  }



  .right .modify:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .return:hover {
    cursor: pointer;
    opacity: 0.7;
  }

    .right .save {
    position: absolute;
    font-size: 17px;
    left: 100px;
    bottom: 20px;
    width: 200px;
    height: 40px;
    background-color: #3182ce;
    color: #fff;
    border: none;
    border-radius: 7px;
  }

  .right .save:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .show_picture img {
    position: absolute;
    top: 290px;
    left: 150px;
    width: 90px;
    height: 90px;
    border-radius: 50%;
  }

  .right .show_picture img:hover {
    cursor: pointer;
    opacity: 0.7;
  }

  .right .show_file {
    position: absolute;
    left: 260px;
    top: 620px;
  }
</style>