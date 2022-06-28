<template>
    <a type="button" class="btn-link" @click="this.$router.push({ name: 'Home' })">Back</a>

    <h1>New simulation</h1>

    <div class="container-fluid">
        <form class="text-start">
            <div class="mb-3">
                <label class="form-label" for="crop">Crop type</label>
                <div class="d-block row button-carousel overflow-scroll text-nowrap">
                    <div class="d-inline-block col-3 text-center" v-for="(crop, i) in crops" :key="i">
                        <input type="radio" class="btn-check" name="crop type" :id="crop"
                               v-model="crop_type" :value="crop" autocomplete="off">
                        <label class="btn btn-success" :for="crop">
                            <img :src="require(`../assets/${crop}.svg`)" :alt="crop" class="m-2" width="30"/>
                        </label>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <label class="form-label" for="crop">Crop stage</label>
                <div class="d-block row button-carousel overflow-scroll text-nowrap">
                    <div class="d-inline-block col-3" v-for="(stage, i) in stages" :key="i">
                        <input type="radio" class="btn-check" name="crop stage" :id="stage"
                               v-model="crop_stage" :value="i" autocomplete="off">
                        <label class="btn btn-success" :for="stage">
                            <img :src="require(`../assets/crop stages/${stage}.svg`)" :alt="stage" class="m2" width="45"/>
                        </label>
                    </div>
                </div>
            </div>

            <div class="mb-3">
                <label class="form-label" for="startDate">Start date</label>
                <input id="startDate" class="form-control" type="date" v-model="start_date">
            </div>

            <div class="mb-3">
                <label class="form-label" for="endDate">Estimated harvest date</label>
                <input id="endDate" class="form-control" type="date" v-model="end_date" disabled>
            </div>

            <label for="maxWater" class="form-label">Maximum water capacity</label>
            <div class="input-group mb-3">
                <input type="number" class="form-control" id="maxWater" aria-describedby="maxWater" v-model="max_water">
                <span class="input-group-text" id="water-addon">Liters</span>
            </div>

            <label for="fieldSize" class="form-label">Field size</label>
            <div class="input-group mb-3">
                <input type="number" class="form-control" id="fieldSize" aria-describedby="fieldSize"
                       v-model="field_size">
                <span class="input-group-text" id="size-addon">m<sup>2</sup></span>
            </div>

            <a class="btn btn-primary" type="submit" @click="create_simulation()">Run simulation</a>
        </form>
    </div>
</template>

<script>
import axios from 'axios';
import moment from 'moment';

export default {
    name: 'NewSimulationForm',
    data() {
        return {
            crops: ['Maize', 'Tomato', 'DryBean'],
            stages: ['emergence', 'anthesis', 'max rooting depth', 'canopy senescence'],
            crop_type: null,
            crop_stage: null,
            start_date: null,
            end_date: null,
            max_water: 0,
            field_size: 0
        }
    },
    methods: {
        create_simulation() {
            axios.post('http://localhost:5555/create-simulation', {
                crop_type: this.crop_type,
                crop_stage: this.crop_stage,
                start_date: moment(this.start_date).format('YYYY/MM/DD'),
                end_date: moment(this.end_date).format('YYYY/MM/DD'),
                max_water: this.max_water,
                field_size: this.field_size
            })
            .then(res => {
                console.log(res)
                this.$router.push({name: 'Irrigation schedule', params: {uid: res.data}})
            })
        },
        get_crop_harvest_time() {
            axios.get(`http://localhost:5555/get-crop-harvest/${this.crop_type}`)
            .then(res => {
                console.log(res.data);
                this.end_date = moment(this.start_date).add(res.data, 'days').toISOString().substring(0, 10);
            });
        }
    },
    watch: {
        crop_type: {
            handler(v) {
                if (v && this.start_date) this.get_crop_harvest_time();
            }
        },
        start_date: {
            handler(v) {
                if (v && this.start_date) this.get_crop_harvest_time();
            }
        }
    }
}
</script>

<style>
.btn-check:checked + label > img {
    transform: scale(1.25);
    opacity: 0.3;
    border: none;
}

.col-3 img {
    cursor: pointer;
    transition: transform 1s;
    object-fit: cover;
}

.col-3 label {
    overflow: hidden;
    position: relative;
}
</style>