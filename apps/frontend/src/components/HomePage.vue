<template>
    <h1>Irrigation</h1>
    <div class="container">
        <div class="row row-cols-lg-auto g-3">
            <div class="col-12">
                <button type="button" class="form-control btn btn-danger"
                        @click="this.$router.push({ name: 'Create simulation' })">
                    New
                </button>
            </div>
            <div class="col-3" v-for="(sim, i) in simulations" :key="i">
                <button type="button" class="form-control btn btn-primary" @click="openSimulation(sim.id)">
                    {{ sim.crop_type }}
                </button>
            </div>
        </div>
    </div>
</template>

<script>
import axios from 'axios';

export default {
    async created() {
        await axios.get('http://localhost:5555/get-simulations')
            .then(res => {
                this.simulations = res.data
                console.log(this.simulations);
            })
    },
    data() {
        return {
            simulations: []
        }
    },
    methods: {
        openSimulation(uid) {
            this.$router.push({ name: 'Irrigation schedule', params: { uid: uid } })
        }
    }
}
</script>
