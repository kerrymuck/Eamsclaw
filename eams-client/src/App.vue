<template>
  <router-view />
</template>

<script setup lang="ts">
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background: #f5f5f5;
}

#app {
  width: 100%;
  height: 100vh;
  max-width: 480px;
  margin: 0 auto;
  background: #fff;
}

@media (min-width: 481px) {
  #app {
    max-width: 100%;
  }
}
</style>
