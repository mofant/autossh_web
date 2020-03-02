<template>
	<section>
		<!--工具条-->
		<el-col :span="24" class="toolbar" style="padding-bottom: 0px;">
			<el-form :inline="true" :model="filters">
				<el-form-item>
					<el-input v-model="filters.name" placeholder="代理名称"></el-input>
				</el-form-item> 
				<el-form-item>
					<el-button type="primary" v-on:click="getProxys">查询</el-button>
				</el-form-item> 
				<el-form-item>
					<el-button type="primary" @click="handleAdd">新增</el-button>
				</el-form-item>
			</el-form>
		</el-col>

		<!--列表-->
		<el-table :data="proxys" highlight-current-row v-loading="listLoading" @selection-change="selsChange" style="width: 100%;">
			<el-table-column type="selection" width="55">
			</el-table-column>
			<el-table-column type="index" width="40">
			</el-table-column>
			<el-table-column prop="service_name" label="服务名称" width="150" sortable>
			</el-table-column>
			<el-table-column prop="server_name" label="代理服务器" width="150" sortable>
			</el-table-column>
			<el-table-column prop="proxy_port" label="代理端口" width="150" sortable>
			</el-table-column>
			<el-table-column prop="state" label="状态" width="150" :formatter="formatProxyState" sortable>
			</el-table-column>
			<el-table-column prop="run_state" label="运行状态" width="150"  sortable>
			</el-table-column>
			<el-table-column label="操作" width="300">
				<template scope="scope">
					<el-button type="primary" size="small" @click="handleRefresh(scope.$index, scope.row)">刷新</el-button>
					<el-button type="success" size="small" @click="handleStart(scope.$index, scope.row)">启动</el-button>
					<el-button type="warning" size="small" @click="handleStop(scope.$index, scope.row)">停止</el-button>
					<el-button type="danger" size="small" @click="handleDel(scope.$index, scope.row)">删除</el-button>
				</template>
			</el-table-column>
		</el-table>

		<!--工具条-->
		<el-col :span="24" class="toolbar">
			<el-button type="danger" @click="batchRemove" :disabled="this.sels.length===0">批量删除</el-button>
			<el-pagination layout="prev, pager, next" @current-change="handleCurrentChange" :page-size="20" :total="total" style="float:right;">
			</el-pagination>
		</el-col>

		<!--编辑界面-->
		<el-dialog title="编辑" :visible.sync="editFormVisible" :close-on-click-modal="false">
			<el-form :model="editForm" label-width="130px" ref="editForm">
				<el-form-item label="服务名称" prop="name">
					<el-input v-model="editForm.name" auto-complete="off"></el-input>
				</el-form-item>
				<el-form-item label="服务端口">
					<el-input v-model="editForm.port" ></el-input>
				</el-form-item>
				<el-form-item label="所在服务器">
					<el-select v-model="editForm.dep_server" placeholder="请选择">
                        <el-option
                            v-for="item in servers"
                            :key="item.id"
                            :label="item.name"
                            :value="item.id">
                        </el-option>
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
			<el-form :model="addForm" label-width="130px" ref="addForm">
<!-- ASDF -->
				<el-form-item label="服务名称">
					<el-select v-model="addForm.service" placeholder="请选择">
                        <el-option
                            v-for="item in services"
                            :key="item.id"
                            :label="item.name"
                            :value="item.id">
                        </el-option>
				    </el-select>
				</el-form-item>
				<el-form-item label="代理服务器">
					<el-select v-model="addForm.proxy_server" placeholder="请选择">
                        <el-option
                            v-for="item in servers"
                            :key="item.id"
                            :label="item.name"
                            :value="item.id">
                        </el-option>
				    </el-select>
				</el-form-item>
				<el-form-item label="代理端口">
					<el-input v-model="addForm.proxy_port" ></el-input>
				</el-form-item>
				<el-form-item label="启用Supervisor">
					<el-switch on-text="" off-text="" v-model="addForm.dep_supervisor"></el-switch>
				</el-form-item>
				<el-form-item label="对外开放端口">
					<el-switch on-text="" off-text="" v-model="addForm.open_port"></el-switch>
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
	import Vue from 'vue'
	import util from '../../common/js/util'
	import { getProxyList, createProxy, modifyProxy, delProxy } from '../../api/api';
	import { getServerList } from '../../api/api';
	import { getServiceList } from '../../api/api';
	import { refreshProxy, startProxy, stopProxy, deleteProxy } from "../../api/api";

	export default {
		data() {
			return {
				filters: {
					name: ''
				},
				proxys: [],
				servers: [],
				services: [],
				total: 0,
				page: 1,
				listLoading: false,
				sels: [],//列表选中列

				editFormVisible: false,//编辑界面是否显示
				editLoading: false,

				//编辑界面数据
				editForm: {
					port: 22,
					server: '',
					service: ''
				},
				addFormVisible: false,//新增界面是否显示
				addLoading: false,

				//新增界面数据
				addForm: {
					proxy_port: 22,
					proxy_server: '',
					service: '',
					dep_supervisor: false,
					open_port: false
				},
				proxyState: {
					DEPLOYED: "已经部署",
        			CREATED: "已创建"
				},
			}
		},
		methods: {

			getProxys() {
				let para = {
					page_num: this.page,
					name: this.filters.name
                };
                this.listLoading = true;
                getProxyList(para).then((res) => {
					this.total = 10;
					res.data.data.forEach( proxy => {
						proxy.run_state = "";
					});
					this.proxys = res.data.data;
					this.listLoading = false;
                });
			},

            //获取服务器列表
            getServers() {
                let para = {
                    page_num: this.page,
					name: this.filters.name
                };
                this.listLoading = true;
                getServerList(para).then((res) => {
					this.total = 10;
					this.servers = res.data.data;
					this.listLoading = false;
                });
			},
			// 获取服务列表
			getServices() {
				let para = {
                    page_num: this.page,
					name: this.filters.name
                };
                this.listLoading = true;
                getServiceList(para).then((res) => {
					this.total = 10;
					this.services = res.data.data;
					this.listLoading = false;
                });
			},
			//显示转换
			formatProxyState(row, colunn) {
				return this.proxyState[row.state];
			},
			handleCurrentChange(val) {
				this.page = val;
				this.getUsers();
            },

			// 刷新状态
			handleRefresh: function(index, row) {
				let para = { id: row.id };
				refreshProxy(para).then((res) =>{
					console.log(res);
					if( res.data.code == 200 ) {
						this.proxys[index].run_state = res.data.data.state;
					}
					this.$message({
							message: '刷新成功',
							type: 'success'
					});
				});
			},
			handleStart: function(index, row) {
				let para = { id: row.id };
				startProxy(para).then((res) => {
					console.log(res);
					if( res.data.code == 200 ) {
						this.$message({
							message: "任务状态:" + res.data.data.state,
							type: 'success'
						});
						this.proxys[index].run_state = res.data.data.state;
					}else{
						this.$message({
						message: res.data.msg,
						type: 'error'
					});
					}
					
				});
				console.log("启动");
			},
			handleStop: function(index, row) {
				console.log("停止");
				let para = { id: row.id };
				stopProxy(para).then((res) => {
					console.log("finish stop");
					if(res.data.code == 200){
						this.$message({
							message: "任务状态:" + res.data.data.state,
							type: 'success'
						});
						this.proxys[index].run_state = res.data.data.state;
					}else{
						this.$message({
							message: res.data.msg,
							type: 'error'
						});
					}
				});
			},
			//删除
			handleDel: function (index, row) {
				this.$confirm('确认删除该记录吗?', '提示', {
					type: 'warning'
				}).then(() => {
					this.listLoading = true;
					//NProgress.start();
					let para = { id: row.id };
					deleteProxy(para).then((res) => {
						if(res.data.code == 200){
							this.$message({
								message: '卸载服务成功',
								type: 'success'
							});
							delProxy(para).then((res) => {
								this.listLoading = false;
								this.$message({
									message: '删除成功',
									type: 'success'
								});
								this.getProxys();
							});
						}else{
							this.$message({
								message: res.data.msg,
								type: 'error'
							});
							this.$confirm("是否删除", "提示", {
								type: 'warning'
							}).then(() => {
								delProxy(para).then((res) => {
								this.listLoading = false;
								this.$message({
									message: '删除成功',
									type: 'success'
								});
								});
								this.getProxys();
							});
						}
					});
				}).catch(() => {

				});
			},
			//显示编辑界面
			handleEdit: function (index, row) {
				this.editFormVisible = true;
				this.editForm = Object.assign({}, row);
			},
			//显示新增界面
			handleAdd: function () {
				this.getProxys();
				this.addFormVisible = true;
				this.addForm = {
					port: 22,
					server: '',
					service: '',
					dep_supervisor: false,
					open_port: false
				};
			},
			//编辑
			editSubmit: function () {
				this.$refs.editForm.validate((valid) => {
					if (valid) {
						this.$confirm('确认提交吗？', '提示', {}).then(() => {
							this.editLoading = true;
							//NProgress.start();
							let para = Object.assign({}, this.editForm);
							console.log(para);
							modifyProxy(para).then((res) => {
								this.editLoading = false;
								this.$message({
									message: '提交成功',
									type: 'success'
								});
								this.$refs['editForm'].resetFields();
								this.editFormVisible = false;
								this.getProxys();
							});
						});
					}
				});
			},
			//新增
			addSubmit: function () {
				this.$refs.addForm.validate((valid) => {
					if (valid) {
						this.$confirm('确认提交吗？', '提示', {}).then(() => {
							this.addLoading = true;
							//NProgress.start();
							let para = Object.assign({}, this.addForm);
							//para.birth = (!para.birth || para.birth == '') ? '' : util.formatDate.format(new Date(para.birth), 'yyyy-MM-dd');
							createProxy(para).then((res) => {
								this.addLoading = false;
								//NProgress.done();
								res = res.data
								console.log(res);
								if (res.code == 500) {
										this.$message({
										message: res.msg,
										type: 'error'
									});
								}else{
									this.$message({
										message: '提交成功',
										type: 'success'
									});
									this.$refs['addForm'].resetFields();
									this.addFormVisible = false;
									this.getProxys();
								}

							});
						});
					}
				});
			},
			selsChange: function (sels) {
				this.sels = sels;
			},
			//批量删除
			batchRemove: function () {
				var ids = this.sels.map(item => item.uid)
				console.log(ids)
				this.$confirm('确认删除选中记录吗？', '提示', {
					type: 'warning'
				}).then(() => {
					this.listLoading = true;
					//NProgress.start();
					// let para =  {uids: ids} ;
					batchDel(ids).then((res) => {
						this.listLoading = false;
						//NProgress.done();
						this.$message({
							message: '删除成功',
							type: 'success'
						});
						this.getProxys();
					});
				}).catch(() => {

				});
			}
		},
		mounted() {
			this.getServers();
			this.getServices();
			this.getProxys();
		}
	}

</script>

<style scoped>

</style>