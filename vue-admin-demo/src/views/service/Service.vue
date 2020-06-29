<template>
  <section>
    <!--工具条-->
    <el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
      <el-form :inline="true" :model="filters">
        <!-- <el-form-item>
          <el-input v-model="filters.name" placeholder="服务名称"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" v-on:click="getServices">查询</el-button>
        </el-form-item> -->
        <el-form-item>
          <el-button type="primary" @click="handleAdd">新增</el-button>
        </el-form-item>
      </el-form>
    </el-col>

    <!--列表-->
    <el-table
      :data="services"
      highlight-current-row
      v-loading="listLoading"
      @selection-change="selsChange"
      style="width: 100%;"
    >
      <el-table-column type="selection" width="55"></el-table-column>
      <el-table-column type="index" width="60"></el-table-column>
      <el-table-column prop="name" label="服务名称" width="200" sortable></el-table-column>
      <el-table-column prop="server_name" label="服务部署服务器" width="200" sortable></el-table-column>
      <el-table-column prop="port" label="服务端口" width="200" sortable></el-table-column>
      <el-table-column label="操作" width="150">
        <template scope="scope">
          <el-button size="small" @click="handleEdit(scope.$index, scope.row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!--工具条-->
    <el-col :span="24" class="toolbar">
      <!-- <el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button> -->
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
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="editForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="服务端口">
          <el-input v-model="editForm.port"></el-input>
        </el-form-item>
        <el-form-item label="所在服务器">
          <el-select v-model="editForm.dep_server" placeholder="请选择">
            <el-option v-for="item in servers" :key="item.id" :label="item.name" :value="item.id"></el-option>
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
        <el-form-item label="服务名称" prop="name">
          <el-input v-model="addForm.name" auto-complete="off"></el-input>
        </el-form-item>
        <el-form-item label="服务端口">
          <el-input v-model="addForm.port"></el-input>
        </el-form-item>
        <el-form-item label="所在服务器">
          <el-select v-model="addForm.dep_server" placeholder="请选择">
            <el-option v-for="item in servers" :key="item.id" :label="item.name" :value="item.id"></el-option>
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
import {
  getServiceList,
  createService,
  modifyService,
  delService,
  delServer
} from "../../api/api";
import { getServerList } from "../../api/api";

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
      filters: {
        name: ""
      },
      servers: [],
      services: [],
      total: 0,
      page: 1,
      limit: 10,
      offset: 0,
      listLoading: false,
      sels: [], //列表选中列

      editFormVisible: false, //编辑界面是否显示
      editLoading: false,
      editFormRules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }]
      },
      //编辑界面数据
      editForm: {
        name: "",
        port: 22,
        dep_server: "",
        server_name: ""
      },

      addFormVisible: false, //新增界面是否显示
      addLoading: false,
      addFormRules: {
        name: [{ required: true, message: "请输入姓名", trigger: "blur" }]
      },
      //新增界面数据
      addForm: {
        name: "",
        port: 22,
        dep_server: ""
      }
    };
  },
  methods: {
    //性别显示转换
    formatServerType(row, colunn) {
      return this.server_type_format[row.server_type];
    },

    getServices() {
      var offset = (this.page - 1) * this.limit;
      let para = {
        page: this.page,
        name: this.filters.name,
        limit: this.limit,
        offset: offset,
      };
      this.listLoading = true;
      getServiceList(para).then(res => {
        this.total = res.data.data.count;
        this.services = res.data.data.results;
        this.listLoading = false;
      });
    },

    handleCurrentChange(val) {
      this.page = val;
      this.getServices();
    },
    //获取服务器列表
    getServers() {
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
    //删除
    handleDel: function(index, row) {
      this.$confirm("确定一并停止并删除已有代理吗?", "提示", {
        type: "warning"
      })
        .then(() => {
          this.listLoading = true;
          //NProgress.start();
          let para = { id: row.id };
          delService(para).then(res => {
            this.listLoading = false;
            //NProgress.done();
            this.$message({
              message: "删除成功",
              type: "success"
            });
            this.getServices();
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
      this.getServices();
      this.addFormVisible = true;
      this.addForm = {
        name: "",
        port: 22,
        dep_server: ""
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
            console.log(para);
            modifyService(para).then(res => {
              this.editLoading = false;
              this.$message({
                message: "提交成功",
                type: "success"
              });
              this.$refs["editForm"].resetFields();
              this.editFormVisible = false;
              this.getServices();
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
            let para = Object.assign({}, this.addForm);
            createService(para).then(res => {
              this.addLoading = false;
              res = res.data;
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
                this.getServices();
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
    // batchRemove: function() {
    //   var ids = this.sels.map(item => item.uid);
    //   console.log(ids);
    //   this.$confirm("确认删除选中记录吗？", "提示", {
    //     type: "warning"
    //   })
    //     .then(() => {
    //       this.listLoading = true;
    //       //NProgress.start();
    //       // let para =  {uids: ids} ;
    //       batchDel(ids).then(res => {
    //         this.listLoading = false;
    //         //NProgress.done();
    //         this.$message({
    //           message: "删除成功",
    //           type: "success"
    //         });
    //         this.getServerList();
    //       });
    //     })
    //     .catch(() => {});
    // }
  },
  mounted() {
    this.getServices();
    this.getServers();
  }
};
</script>

<style scoped>
</style>