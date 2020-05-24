<template>
  <section>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters">
        <el-form-item>
          <el-input v-model="filters.name" placeholder="服务器名称"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" v-on:click="getServerList">查询</el-button>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleAdd">新增</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table
      :data="servers"
      highlight-current-row
      v-loading="listLoading"
      @selection-change="selsChange"
      style="width: 100%;"
    >
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column type="index" width="60"></el-table-column>
      <el-table-column prop="name" label="服务器名称" width="200" sortable></el-table-column>
      <el-table-column prop="host" label="服务器地址" width="200" sortable></el-table-column>
      <el-table-column
        prop="server_type"
        label="服务器类型"
        width="200"
        :formatter="formatServerType"
        sortable
      ></el-table-column>
      <el-table-column label="操作" width="150">
        <template scope="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--工具条-->
    <el-col :span="24" class="toolbar">
      <el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>
      <el-pagination
        layout="prev, pager, next"
        @current-change="handleCurrentChange"
        :page-size="10"
        :total="total"
        style="float:right;"
      ></el-pagination>
    </el-col>

    <!--编辑界面-->
    <el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false">
      <el-form :model="editForm" label-width="130px" :rules="editFormRules" ref="editForm">
        <el-form-item label="服务器名称" prop="name">
          <el-input v-model="editForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="服务器IP地址">
          <el-input v-model="editForm.host"></el-input>
        </el-form-item>
        <el-form-item label="服务器登录用户名">
          <el-input v-model="editForm.username"></el-input>
        </el-form-item>
        <el-form-item label="服务器登录密码">
          <el-input v-model="editForm.password"></el-input>
        </el-form-item>
        <el-form-item label="服务器SSH端口">
          <el-input v-model="editForm.port"></el-input>
        </el-form-item>
        <el-form-item label="服务器类型">
          <el-select v-model="editForm.server_type" placeholder="请选择">
            <el-option
              v-for="item in server_types"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="操作系统">
          <el-select v-model="editForm.system_type" placeholder="请选择">
            <el-option
              v-for="item in system_types"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="editFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="editSubmit" :loading="editLoading">提交</el-button>
      </div>
    </el-dialog>

    <!--新增界面-->
    <el-dialog title="新增" :visible.sync="addFormVisible" :close-on-click-modal="false">
      <el-form :model="addForm" label-width="130px" :rules="addFormRules" ref="addForm">
        <!-- ASDF -->
        <el-form-item label="服务器名称" prop="name">
          <el-input v-model="addForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="服务器IP地址">
          <el-input v-model="addForm.host" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="服务器登录用户名">
          <el-input v-model="addForm.username"></el-input>
        </el-form-item>
        <el-form-item label="服务器登录密码">
          <el-input v-model="addForm.password"></el-input>
        </el-form-item>
        <el-form-item label="服务器SSH端口">
          <el-input v-model="addForm.port"></el-input>
        </el-form-item>
        <el-form-item label="服务器类型">
          <el-select v-model="addForm.server_type" placeholder="请选择">
            <el-option
              v-for="item in server_types"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="操作系统">
          <el-select v-model="addForm.system_type" placeholder="请选择">
            <el-option
              v-for="item in system_types"
              :key="item.value"
              :label="item.label"
              :value="item.value"
            ></el-option>
          </el-select>
        </el-form-item>
        <!-- ASDF -->
      </el-form>
      <div slot="footer" class="dialog-footer">
        <el-button @click.native="addFormVisible = false">取消</el-button>
        <el-button type="primary" @click.native="addSubmit" :loading="addLoading">提交</el-button>
      </div>
    </el-dialog>
  </section>
</template>

<script>
import util from "../../common/js/util";
//import NProgress from 'nprogress'
import {
  getServerList,
  createServer,
  modifyServer,
  delServer
} from "../../api/api";

export default {
  data() {
    return {
      server_types: [
        { value: "PROXY", label: "代理服务器" },
        { value: "DEPLOY", label: "服务部署服务器" }
      ],
      server_type_format: {
        PROXY: "代理服务器",
        DEPLOY: "服务部署服务器"
      },
      system_types: [
        { value: "UBUNTU", label: "ubuntu" },
        { value: "CENTOS", label: "centos" }
      ],
      filters: {
        name: ""
      },
      servers: [],
      total: 0,
      page: 1,
      listLoading: false,
      sels: [], //列表选中列

      editFormVisible: false, //编辑界面是否显示
      editLoading: false,
      editFormRules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        host: [{ required: true, message: "请输入IP", trigger: "blur" }]
      },
      //编辑界面数据
      editForm: {
        password: "",
        name: "",
        host: "",
        port: 22,
        username: "",
        server_type: "",
        system_type: ""
      },

      addFormVisible: false, //新增界面是否显示
      addLoading: false,
      addFormRules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }],
        host: [{ required: true, message: "请输入IP", trigger: "blur" }]
      },
      //新增界面数据
      addForm: {
        password: "",
        name: "",
        host: "",
        port: 22,
        username: "",
        server_type: "",
        system_type: ""
      }
    };
  },
  methods: {
    //性别显示转换
    formatServerType(row, colunn) {
      return this.server_type_format[row.server_type];
    },
    handleCurrentChange(val) {
      this.page = val;
      this.getServerList();
    },
    //获取服务器列表
    getServerList() {
      let para = {
        page: this.page,
        name: this.filters.name
      };
      this.listLoading = true;
      getServerList(para).then(res => {
        this.total = res.data.data.count;
        this.servers = res.data.data.results;
        this.listLoading = false;
      });
    },
    handleDel: function(index, row) {
      this.$confirm("将一并删除服务和代理?", "提示", {
        type: "warning"
      })
        .then(() => {
          this.listLoading = true;
          //NProgress.start();
          //let para = { uid: row.uid };
          delServer(row).then(res => {
            this.listLoading = false;
            //NProgress.done();
            this.$message({
              message: "删除成功",
              type: "success"
            });
            this.getServerList();
          });
        })
        .catch(() => {});
    },
    //显示编辑界面
    handleEdit: function(index, row) {
      this.editFormVisible = true;
      this.editForm = Object.assign({}, row);
    },
    //显示新增界面
    handleAdd: function() {
      this.getServerList();
      this.addFormVisible = true;
      this.addForm = {
        password: "",
        name: "",
        host: "",
        port: 22,
        username: "",
        server_type: ""
      };
    },
    //编辑
    editSubmit: function() {
      this.$refs.editForm.validate(valid => {
        if (valid) {
          this.$confirm("确认提交吗？", "提示", {}).then(() => {
            this.editLoading = true;
            //NProgress.start();
            let para = Object.assign({}, this.editForm);
            // para.birth = (!para.birth || para.birth == '') ? '' : util.formatDate.format(new Date(para.birth), 'yyyy-MM-dd');
            modifyServer(para).then(res => {
              this.editLoading = false;
              if (res.data.code === 200) {
                this.$message({
                  message: "提交成功",
                  type: "success"
                });
                this.$refs["editForm"].resetFields();
                this.editFormVisible = false;
                this.getServerList();
              } else {
                this.$message({
                  message: res.data.msg,
                  type: "error"
                });
              }
            });
          });
        }
      });
    },
    //新增
    addSubmit: function() {
      this.$refs.addForm.validate(valid => {
        if (valid) {
          this.$confirm("确认提交吗？", "提示", {}).then(() => {
            this.addLoading = true;
            //NProgress.start();
            let para = Object.assign({}, this.addForm);
            //para.birth = (!para.birth || para.birth == '') ? '' : util.formatDate.format(new Date(para.birth), 'yyyy-MM-dd');
            createServer(para).then(res => {
              this.addLoading = false;
              //NProgress.done();
              res = res.data;
              console.log(res);
              if (res.code == 500) {
                this.$message({
                  message: res.msg,
                  type: "error"
                });
              } else {
                this.$message({
                  message: "提交成功",
                  type: "success"
                });
                this.$refs["addForm"].resetFields();
                this.addFormVisible = false;
                this.getServerList();
              }
            });
          });
        }
      });
    },
    selsChange: function(sels) {
      this.sels = sels;
    },
    //批量删除
    batchRemove: function() {
      var ids = this.sels.map(item => item.uid);
      console.log(ids);
      this.$confirm("确认删除选中记录吗？", "提示", {
        type: "warning"
      })
        .then(() => {
          this.listLoading = true;
          //NProgress.start();
          // let para =  {uids: ids} ;
          batchDel(ids).then(res => {
            this.listLoading = false;
            //NProgress.done();
            this.$message({
              message: "删除成功",
              type: "success"
            });
            this.getServerList();
          });
        })
        .catch(() => {});
    }
  },
  mounted() {
    this.getServerList();
  }
};
</script>

<style scoped>
</style>