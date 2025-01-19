<template>
  <div>
    <img src="../public/logo.png" alt=""></img>
  </div>
  <div class="dashboard">
    <div class="header">
      <h2>数据概览</h2>
    </div>
    <div class="stats-grid">
      <div class="stat-card" v-for="(stat, index) in stats" :key="index">
        <div class="stat-title">{{ stat.title }}</div>
        <div class="stat-value">
          <div v-for="(item, idx) in stat.items" :key="idx">{{ item }}</div>
        </div>
      </div>
    </div>
    <div class="control_card">
      <div class="img"></div>
      <div class="ctrl_button">
        <button>跳转按钮</button>
        <button>按钮2</button>
        <button>按钮3</button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      systemInfo: null,
      stats: [
        { title: '系统信息', items: [] },
        { title: '网络信息', items: [] },
        { title: '自检信息', items: [] },
      ],
    };
  },
  mounted() {
    axios.get('http://localhost:3000/api/system-info')
        .then(response => {
          this.systemInfo = response.data;
          // 以数组形式更新每项内容
          this.stats[0].items = [
            `系统: ${this.systemInfo.System}`,
            `Python: ${this.systemInfo.Python}`,
            `ROS: ${this.systemInfo.ROS}`
          ];
          this.stats[1].items = [
            `SSID: ${this.systemInfo.SSID}`,
            `信号强度: ${this.systemInfo.Strength}`
          ];
          this.stats[2].items = [
            `自检结果: ${this.systemInfo['Self-test']}`
          ];
        })
        .catch(error => {
          console.error('获取系统信息失败:', error);
        });
  }
};
</script>

<style scoped>

</style>
