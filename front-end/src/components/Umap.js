import { useUmap } from './api_get';
import React, { useEffect, useState } from 'react';

export function Umap({ query, link }) {
    const [umap, setUmap] = useState("");
    const links = useUmap();

    useEffect(() => {
        if (links?.isSuccess && Object.keys(query).length === 0) {
            setUmap(links.data.PDF);
        } else if (links?.isSuccess && links.data?.Query) {
            setUmap(links.data.Query);
        }

        if (link !== "")
            setUmap(link["Query"]);

    }, [link, query, links]);

    return (umap ? <img src={umap} alt='immagine umap' className='umap-img' /> : <div className='no_umap'>NO UMAP</div>);
}
