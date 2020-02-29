//test
export const increment = ({commit}) => {
    commit('INCREMENT')
}
export const decrement = ({commit}) => {
    commit('DECREMENT')
}


export const set_token = (context,token) => {
    context.commit("set_token",token);
}

export const del_token = context => {
    context.commit("del_token");
}