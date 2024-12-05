// src/components/AttributionVisualization.tsx

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
// import { fetchAttributions } from '../services/apiService';

const AttributionVisualization: React.FC = () => {
    const [attributions, setAttributions] = useState<any[]>([]);
    const svgRefs = useRef<(SVGSVGElement | null)[]>([]);


    // useEffect(() => {
    //     const loadData = async () => {
    //         try {
    //             const attributionsData = await fetchAttributions();
    //             setAttributions(attributionsData);
    //         } catch (error) {
    //             console.error("Error loading attributions:", error);
    //         }
    //     };
    //     loadData();
    // }, []);

    const renderCharts = () => {
        attributions.forEach((attribute, index) => {
            const svg = d3.select(svgRefs.current[index])
                .attr("width", 300)
                .attr("height", 300);

            // Clear previous elements
            svg.selectAll("*").remove();

            if (attribute.type === 'line') {
                // Draw line chart
                const xScale = d3.scaleLinear()
                    .domain([0, attribute.values.length - 1])
                    .range([0, 280]);

                const numericValues = attribute.values
                    .map((value: string) => parseFloat(value))
                    .filter((val: number) => !isNaN(val)) as number[];
                
                const yScale = d3.scaleLinear()
                    .domain([d3.min(numericValues)!, d3.max(numericValues)!])
                    .range([280, 20]);
                
                const line = d3.line<number>()
                    .x((_, i) => xScale(i))
                    .y(d => yScale(d));

                svg.append("path")
                    .datum(attribute.values)
                    .attr("fill", "none")
                    .attr("stroke", "steelblue")
                    .attr("stroke-width", 2)
                    .attr("d", line);
            }
            // Additional chart types here: e.g., pie, bar
        });
    };

    useEffect(() => {
        if (attributions.length) renderCharts();
    }, [attributions]);

    return (
        <div>
            {attributions.map((attribute, index) => (
                <div key={index}>
                    <h3>{attribute.name}</h3>
                    <svg ref={el => (svgRefs.current[index] = el!)} width="300" height="300"></svg>
                </div>
            ))}
        </div>
    );
};

export default AttributionVisualization;
