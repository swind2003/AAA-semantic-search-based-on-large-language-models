<template>
  <div class="wrapped-cr"  v-loading="loading" element-loading-text="上传资料中" element-loading-spinner="el-icon-loading" element-loading-background="rgba(0, 0, 0, 0.8)">
    <div class="left">
      <ul class="leftText">
        <!-- <li><h2>当前登录人：{{loginname}}</h2></li> -->
        <li class="one">修改角色</li>
        <li class="two" @click='toCreateInnerRoles()'>新增角色</li>
        <li class="three" @click="exit()">退出登录</li>
      </ul>
    </div>
    <div class="right">
      <div class="top-cr">
        <h2>内置角色列表</h2>
         <el-button type="text" @click="open" class='changeKey'>修改API密钥</el-button>
      </div>
      <div class="roleTable">
        <table>
          <thead>
            <tr>
              <th style="width: 320px;">头像</th>
              <th style="width: 320px;">名称</th>
              <th style="width: 320px;">描述</th>
              <th style="width: 400px;">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index1) in role_log" :key="index1">
               <td v-for="(picture, index2) in pictures" :key="index2" v-show="index1 === index2" class="imgWrapped">
                <img :src="picture" alt="">
              </td>
              <td>{{item.role_name}}</td>
              <td>{{formatText(item.description) }}</td>
              <td><button class='change' @click="modifyRole(item.role_id)">修改角色</button>
              <input type="file" :ref="'fileInput_' + index1" style="display: none" @change="handleFileUpload(index1, item.role_id)" accept=".txt">
              <button class='uoload' @click="selectAndUploadFile(index1)" :disabled="!item.have_document_store" :class="{ 'disabled-button': !item.have_document_store }">上传资料</button>
              </td>
            </tr>
          </tbody>

        </table>  
               
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'
export default {
  name: 'ChangeRole',
  data() {
        return {
          role_log: [],
          user_id: this.$route.query.user_id,
          text: '的海外的合法大大覅哈哈爱上的人发放时aaa',
          pictures: [], // 头像
          role_id: [],
          file: null, // 上传的AI资料
          selectedFile: null, // 用于存储用户选择的文件
          file_get: '', // 上传的AI资料
          file_show: '', // 上传的资料名称显示
          loading: false,
          loginname: ''

        }
      },
  
   created () {
    document.title = '内置角色列表-chataaa'
    this.getInfo()
  },

  mounted () {
    this.loginname = this.cookie.getCookie('LoginName')
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



    selectAndUploadFile(index) {
    // 触发文件选择
    this.$refs['fileInput_' + index][0].click();
  },

  handleFileUpload(index, roleId) {
    // 处理文件选择事件
    const file = this.$refs['fileInput_' + index][0].files[0];


    // 检查文件类型是否为 .txt
    if (file && file.type === 'text/plain') {
    // 执行文件上传操作，可以调用你之前的上传逻辑
    this.uploadFile(file, roleId);
    this.$refs['fileInput_' + index][0].value = '';
    // this.loading = true
    } else {
    // 如果不是 .txt 文件，清空选择的文件或者进行其他处理
    this.$message({
          message: '请选择一个 .txt 文件',
          type: 'warning'
        });
    }
  },
   
   async uploadFile(file, roleId) {
    // 执行文件上传的逻辑，可以使用 XMLHttpRequest 或其他上传方式
    // 请根据你的实际需求进行实现
    let files = new FormData()
    files.append('files', file)
    files.append('role_id', roleId)
    this.loading = true
    const res = await axios.post('http://8.134.178.190:5000//builtin_role_administrator/add_role_store', files) 
    this.loading = false
    if (res.data.code === '200') {
      this.$message({
          message: '上传成功！',
          type: 'success'
        });
    } else if (res.data.code === '400' || res.data.code === '401') {
      this.$message.error('上传失败！');
    }
  },

  
    formatText(text) {
    if (text.length > 18) {
    return `${text.slice(0, 18)}...`;
    }
    return text;
  },
    async getInfo () {
      const res1 = await axios.get('http://8.134.178.190:5000/builtin_role_administrator/information/get_role_information', {
        params: {
          user_id: "000000"
        }
      })
      // console.log(this.user_id);
      // console.log(res1);
      this.role_log = res1.data.data
      // console.log(this.role_log);
      this.getPictures(this.role_log)
  },

  async getPictures (role_log) {
      this.pictures = []
      let length = role_log.length
      for (let i = 0 ; i < length; i++) {
        const res = await axios.get('http://8.134.178.190:5000/builtin_role_administrator/information/get_role_head_portrait', {
          params: {
            role_id: role_log[i].role_id,
            user_id: "000000"
          },
          responseType: 'blob'
        })
        if (res.data.code === '400' ) {
      this.$message.error('获取头像失败！');
        }
        const imgUrl = URL.createObjectURL(res.data)
        this.pictures.push(imgUrl)
      }
    },

    async modifyRole (roleId) {
    this.$router.push({
        path: '/ModifyRole',
        query: {
              user_id: this.user_id,
              role_id: roleId,
            }
      })
    },

    async sendAPI (value) {
      const res = await axios.get('http://8.134.178.190:5000//builtin_role_administrator/information/write_openai_api_key', {
          params: {
            openai_api_key: value,
          },
        })

        if (res.data.code === '200') {
      this.$message({
          message: '上传成功！',
          type: 'success'
        });
    } else if (res.data.code === '400') {
      this.$message.error('上传失败！');
    }
      // console.log(res);
    },

     open() {
        this.$prompt('请输入API密钥', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          inputPattern: /^sk-[a-zA-Z0-9]+$/,
          inputErrorMessage: 'API密钥格式不正确'
        }).then(({ value }) => {
            this.$message({
            type: 'success',
            message: '你的API密钥是: ' + value
          });
          this.sendAPI (value)
        }).catch(() => {
          this.$message({
            type: 'info',
            message: '取消输入'
          });       
        });
      }
              
}
}
</script>

<style scoped>
.wrapped-cr {
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
    width: 1445px;
    background-color: #f2f5f8;
  }



  .top-cr {
    /* display: flex; */
    width: 100%;
    height: 80px;
    border: 1px solid #d3d4d6;
  }

  .top-cr h2 {
    margin-left:600px;
    display: inline-block;
    /* text-align: center; */
    line-height: 80px;
  }

  .top-cr .changeKey {
    margin-left: 500px;
  }



 
  .roleTable {
    margin-left: 20px;
    max-height: 505px; 
    overflow-y: auto;
  }
  .roleTable table {
    border-collapse: collapse;
  }
  
  .roleTable th {
    position: sticky;
    top: 0;
    background-color: #f2f2f2;
    z-index: 1;
  }

  .roleTable th, td {
    text-align: center;
    width: 330px;
    height: 50px;
    border: 1px solid #BBBBBB;
  }
  
   .roleTable .imgWrapped img {
   /* position: absolute; */
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  
  .roleTable .upload {
     width: 90px;
    height: 30px;
    background-color: #9CBFFB;
    margin-right: 30px;
    border: none;
  }
  
  .roleTable .change {
    width: 90px;
    height: 30px;
    color: white;
    background-color: #409eff;
    border: none;
  }

  .roleTable .uoload {
    margin-left: 20px;
    width: 90px;
    height: 30px;
    color: white;
    background-color: #67c23a;
    border: none;
  }
  
  .roleTable button:hover {
    opacity: 0.7;
    cursor: pointer;
  }

  .disabled-button {
    margin-left: 20px;
    width: 90px;
    height: 30px;
    color: white;
    background-color: #67c23a;
    border: none;
    opacity: 0.3;
    pointer-events: none; /* 禁用按钮的交互 */
  }
  

</style>