import axios from "axios";
import { useQuery } from "@tanstack/react-query";

export async function fetchData(apiEndpoint) {
    try {
        const res = await axios.get(apiEndpoint);
        console.debug(`Response from ${apiEndpoint}:`, res);
        return res?.data;
    } catch (error) {
        console.error(`Error fetching data from ${apiEndpoint}:`, error);
        throw error;
    }
};

export function usePdfData() {
    const nod = useQuery({ queryKey: ['repGet'], queryFn: () => fetchData('/hierarchy') });
    const urls = useQuery({ queryKey: ['repUrl'], queryFn: () => fetchData('/url') });

    return { nod, urls };
};

export function useUmap() {
    const link = useQuery({ queryKey: ['repUmap'], queryFn: () => fetchData('/links') });
    return link;
};

export function useBlockGraph() {
    const { data: nodeData, isSuccess } = useQuery({
        queryKey: ['repGetNode'],
        queryFn: async () => await fetchData('/members')
    });

    return { data: nodeData, isSuccess };
};