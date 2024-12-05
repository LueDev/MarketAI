// src/components/FactorImpactChart.tsx

import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';

interface FactorImpactChartProps {
    sector: string;
    dataType: string;
}

const FactorImpactChart: React.FC<FactorImpactChartProps> = ({ sector, dataType }) => {
    const chartRef = useRef<SVGSVGElement | null>(null);
    const [data, setData] = useState<{ factor: string; impact: number }[] | null>(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`http://127.0.0.1:10000/api/data/attributions/${sector.toLowerCase()}/${dataType}`);
                
                if (!response.ok) {
                    throw new Error("Network response was not ok");
                }
                
                const jsonData: number[][] = await response.json();

                // Transform nested array data into summary data for each factor
                const factorImpacts: { factor: string; impact: number }[] = jsonData[0].map((_, colIndex) => {
                    // Calculate the average impact for each "factor" across all entries
                    const averageImpact = jsonData.reduce((sum, row) => sum + row[colIndex], 0) / jsonData.length;
                    return { factor: `Factor ${colIndex + 1}`, impact: averageImpact };
                });

                setData(factorImpacts);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
    }, [sector, dataType]);

    useEffect(() => {
        if (!data) return;

        const width = 400;
        const height = 200;
        const margin = { top: 20, right: 30, bottom: 40, left: 40 };

        d3.select(chartRef.current).selectAll("*").remove();

        const svg = d3.select(chartRef.current)
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", `translate(${margin.left},${margin.top})`);

        const x = d3.scaleBand()
            .domain(data.map(d => d.factor))
            .range([0, width])
            .padding(0.1);

        const y = d3.scaleLinear()
            .domain([0, d3.max(data, d => d.impact) || 0])
            .nice()
            .range([height, 0]);

        svg.selectAll("rect")
            .data(data)
            .join("rect")
            .attr("x", d => x(d.factor)!)
            .attr("y", d => y(d.impact))
            .attr("width", x.bandwidth())
            .attr("height", d => height - y(d.impact))
            .attr("fill", "steelblue");

        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x))
            .selectAll("text")
            .attr("transform", "rotate(-45)")
            .style("text-anchor", "end");

        svg.append("g").call(d3.axisLeft(y));

        svg.append("text")
            .attr("x", width / 2)
            .attr("y", height + margin.bottom - 5)
            .attr("text-anchor", "middle")
            .text("Factors");

        svg.append("text")
            .attr("x", -height / 2)
            .attr("y", -margin.left + 10)
            .attr("transform", "rotate(-90)")
            .attr("text-anchor", "middle")
            .text("Average Impact");

    }, [data]);

    return <svg ref={chartRef} />;
};

export default FactorImpactChart;
