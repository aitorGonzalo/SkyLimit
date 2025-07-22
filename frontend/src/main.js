import Vue from 'vue';
import BodySelector from './components/BodySelector.vue';

if (document.getElementById("app")) {
  new Vue({
    render: h => h(BodySelector),
  }).$mount("#app");
}
