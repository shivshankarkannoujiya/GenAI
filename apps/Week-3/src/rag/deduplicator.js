/*
    Removes duplicate documents across all query result sets.
    Documents retrieved earlier (by the original query) get priority.

    Also filters out low-quality results below a score threshold.
 */

export function deduplicate(allResults, scoreThreshold = 0.3) {
    const seenIds = new Set();
    const uniqueDocs = [];

    for (const resultSet of allResults) {
        for (const doc of resultSet) {
            // Skip low-relevance docs
            if (doc.score < scoreThreshold) continue;

            // Skip duplicates
            if (seenIds.has(doc.id)) continue;

            seenIds.add(doc.id);
            uniqueDocs.push(doc);
        }
    }

    // Sort by score descending — best docs first
    uniqueDocs.sort((a, b) => b.score - a.score);

    console.log(
        `\n[Deduplicator] ${uniqueDocs.length} unique docs after dedup and filtering`
    );

    return uniqueDocs;
}
