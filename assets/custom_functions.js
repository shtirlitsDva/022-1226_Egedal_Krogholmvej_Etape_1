window.myNamespace = Object.assign({}, window.myNamespace, {
    mySubNamespace: {
        style: function(feature) {
            return {
                color: feature.properties.color,
                fillColor: feature.properties.color,
                fillOpacity: 0.5,
                weight: 2
            };
        }
    }
});