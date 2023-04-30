window.myNamespace = Object.assign({}, window.myNamespace, {
    mySubNamespace: {
        style: function(feature) {
            return {
                color: feature.properties.color,
                fillColor: feature.properties.color,
                fillOpacity: 0.5,
                weight: 2
            };
        },
        style_fjv: function(feature){
            if (feature.geometry.type === 'Polygon') {
                return {
                    color: feature.properties.color,
                    fillColor: feature.properties.color,
                    fillOpacity: 1,
                    weight: 1,
                };
            } else if (feature.geometry.type === 'LineString') {
                return {
                    color: feature.properties.color,
                    fillColor: feature.properties.color,
                    fillOpacity: 1,
                    weight: 1
                };
            }
        }
    }
});