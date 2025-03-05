<template>
  <div>
    <label for="year">年份:</label>
    <select id="year" v-model="selectedYear" @change="updateMonths">
      <option v-for="year in availableYears" :key="year">{{ year }}</option>
    </select>

    <label for="month">月份:</label>
    <select id="month" v-model="selectedMonth" @change="updateDays">
      <option v-for="month in availableMonths" :key="month">{{ month }}</option>
    </select>

    <label for="day">天数:</label>
    <select id="day" v-model="selectedDay">
      <option v-for="day in availableDays" :key="day">{{ day }}</option>
    </select>
  </div>
</template>

<script>
export default {
  data() {
  return {
    selectedYear: '', // 选择年份
    selectedMonth: '', // 选择月份
    selectedDay: '', // 选择天数
    availableYears: [],   // 存储可选的年份
    availableMonths: [],  // 存储可选的月份
    availableDays: []   // 存储可选的天数
  };
  },
  mounted() {
  this.updateYears(); // 初始化年份
  this.updateMonths(); // 初始化月份
  this.updateDays(); // 初始化天数
  },
  methods: {
  updateYears() {
    const currentYear = new Date().getFullYear();
    // 如果当前年份不在availableYears中，则添加
    for (let Year = 2023; Year <= currentYear; Year++) {
      this.availableYears.push(Year)
    }
  },
  updateMonths() {
    const months = Array.from({ length: 12 }, (_, index) => index + 1);
    this.availableMonths = months;
    this.selectedMonth = ''; // 重置月份
    this.updateDays(); // 更新天数
  },
  updateDays() {
    const selectedYear = parseInt(this.selectedYear);
    const selectedMonth = parseInt(this.selectedMonth);
    const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
    const days = Array.from({ length: daysInMonth }, (_, index) => index + 1);
    this.availableDays = days;

    // 如果当前选择的天数超过新的天数范围，则重置为最大天数
    if (parseInt(this.selectedDay) > daysInMonth) {
    this.selectedDay = '';
    }
  }
  }
};
</script>

<style scoped>
  .container {
    overflow: auto;
    width: 100px;
    height: 100px;
    background-color: pink;
  }
</style>