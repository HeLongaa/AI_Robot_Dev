<template>
  <div>
    <Line :data="chartData" :options="chartOptions" />
  </div>
</template>

<script>
import { Line } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale } from 'chart.js';

// 注册 chart.js 组件
ChartJS.register(Title, Tooltip, Legend, LineElement, CategoryScale, LinearScale);

export default {
  name: 'LineChart',
  components: {
    Line
  },
  data() {
    return {
      chartData: {
        labels: ['一月', '二月', '三月', '四月', '五月'],
        datasets: [
          {
            label: '示例数据',
            data: [10, 20, 30, 40, 50],
            borderColor: '#42A5F5',
            backgroundColor: 'rgba(66, 165, 245, 0.2)',
            borderWidth: 2
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false
      }
    };
  }
};
</script>
