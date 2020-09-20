<template>
  <div class="tac">
    <!-- <span>滚动加载下拉框选项</span> -->
    <el-select
      v-model="kolId"
      placeholder="请选择"
      @change="searchByKol"
      filterable
      v-loadmore="loadMore"
      @visible-change="hideloadMore"
      remote
      :remote-method="remoteMethod"
      @focus="getSelectValue()"
      clearable
    >
      <el-option
        v-for="item of kolOptions"
        :key="item.id"
        :label="item.name"
        :value="item.id"
      ></el-option>
    </el-select>
  </div>
</template>

<script>
import { getServerList } from "../api/api";
import { getServiceList } from "../api/api";

export default {
  name: "LoadMoreSelect",

  props: {
      getValueAPIName: {
          type: String,
          require: true
      },
      meta: {
          type: String,
          default: null
      },
      kolId: {
          type: Number,
          default: null,
      }
  },
  
  data() {
    return {
      searchKolKeycurrentPage: 1, //开始加载的次数，相当于分页加载
      searchKolKeypageSize: 10, //触底滚动一次加载10条
      searchKolKey: "", //后台关键字的搜索功能
    //   kolId: "",
      kolOptions: []
    };
  },
  mounted() {
    // this.Invert(); //编辑时反显才调用，这里用于模拟才加载就调用
    // console.log("checkout kolIk", this.kolId);
    this.getSelectValue();
  },
  methods: {
    //用于编辑功能的反显
    Invert() {
      this.kolId = -1; //编辑功能时可用于反显赋值，
      this.kolOptions = [{ id: -1, name: "请选择" }]; //需要后台返回select的label和value这条数据拼接上去才能反显成功
    },

    loadMore() {
      this.searchKolKeycurrentPage++;
      this.getSelectValue();
    },
    hideloadMore(val) {
      if (!val) {
        this.searchKolKeycurrentPage = 1;
        this.searchKolKey = "";
      }
    },
    remoteMethod(query) {
      if (query !== "") {
        this.searchKolKeycurrentPage = 1;
        this.kolOptions = [];
        this.searchKolKey = query;
        this.getSelectValue();
      } else {
        console.log("输入框清空啦");
        this.kolOptions = [];
      }
    },
    searchByKol(val) {
      this.kolId = val;
    //   console.log("选到了" + this.kolId);
    let para = {
        "selectValue": this.kolId,
        "meta": this.meta,
        "getValueAPIName": this.getValueAPIName,
    }
      this.$emit('selectChange', para)
    },
    //后台接口获取下拉框选项数据
    getSelectValue() {
      var getValuesApi = null;
      if(this.getValueAPIName == "getServiceList") {
          console.log("getServiceList")
          getValuesApi = getServiceList;
      } 
      else if(this.getValueAPIName == "getServerList") {
          console.log("getServerList")
          getValuesApi = getServerList;
      }else {
          console.log("no a valid callback")
          return;
      }
      var that = this;
    //   console.log("发起后台请求");
    //   console.log(
    //     "传参数：" +
    //       "搜索关键字：" +
    //       that.searchKolKey +
    //       "，分页参数：" +
    //       that.searchKolKeycurrentPage +
    //       "，触底滚动一次加载" +
    //       that.searchKolKeypageSize +
    //       "条"
    //   );
    //   console.log("获取到返回结果时,数据拼接");
      let para = {
          page: that.searchKolKeycurrentPage,
          offset: that.kolOptions.length,
          name: that.searchKolKey
      };
      getValuesApi(para).then(res => {
        let arrrs = [];
        arrrs = that.kolOptions.concat(res.data.data.results);
        let hash = {};
        let arr = arrrs.reduce((preVal, curVal) => {
            hash[curVal.id]
            ? ""
            : (hash[curVal.id] = true && preVal.push(curVal));
            return preVal;
        }, []); //去除userId相同的重复项   

        that.kolOptions = arr;
      });
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
</style>
