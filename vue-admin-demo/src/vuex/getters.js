//test
export const getToken = state => {
    let token = state.token;
    if (token !== null && token !== ""){
        return token;
    } 
    token = localStorage.getItem("token");
    if (token !== null && token !== "" ) { return token; }
    return state.token;}

export const getCount = state => {
    return state.count
}
