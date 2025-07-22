<template>
  <div class="body-selector">
    <vue-body-part-selector 
      :selection.sync="selection"
      @click="handleClick"
      :disabled="disabled"
      :multiple="multiple"
      :body-colour="bodyColour"
      :selection-colour="selectionColour"
    />
    <!-- <p class="mt-3 fw-bold">Parte seleccionada: {{ selection }}</p> --> <!-- 🔴 Comentado -->  </div>
</template>

<script>
import Vue from 'vue';
import VueBodyPartSelector from 'vue-body-part-selector';

export default Vue.extend({
  name: 'BodySelector',
  components: {
    VueBodyPartSelector
  },
  data() {
    return {
      selection: '',
      disabled: false,
      multiple: false,
      bodyColour: "#000000", // ⚫ Negro
      selectionColour: "#FF0000", // 🔴 Rojo
    };
  },
  methods: {
    handleClick(bodyPartClicked) {
      console.log("Parte seleccionada:", bodyPartClicked);
      window.location.href = `/ejercicios/${bodyPartClicked}/`; // 🔥 Redirige a Django
    }
  }
});
</script>

<style scoped>
.body-selector {
  width: 300px;
  height: 420px;
  margin: auto;
  text-align: center;
}

/* 🔹 Ajustar las líneas de separación */
.body-selector svg path {
  stroke: #FFFFFF !important; /* Color de las líneas de separación */
  stroke-width: 3px !important; /* Grosor de las líneas */
}
</style>
