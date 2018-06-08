import sphinxapi
import re


class Search():
    client = None
    _sort = []

    def __init__(self):
        self.client = sphinxapi.SphinxClient()
        self.client.SetServer('container-sphinx', 9312)
        self.client.SetMatchMode(sphinxapi.SPH_MATCH_EXTENDED)
        self.client.SetRankingMode(sphinxapi.SPH_RANK_SPH04)

    def filter_query_string(self, text, enable_star = True, match_any = False):
        text = text.translate({ord('*'): 'x', ord('\0'): ''})
        text = re.sub(r"[^-_\p{L}\p{N}]", ' ', text)
        text = self.client.EscapeString(text)

        if match_any:
            text = '* |'.join(text.split(' ')) + '*'

        if enable_star:
            text = '*'+ text +'*'

        return text

    def sorted_by(self, attr, is_asc = True):
        if isinstance(attr, list):
            for i in attr:
                self.sorted_by(i[0], i[1])
        self._sort.append({
            'attr': attr,
            'type': 'ASC' if is_asc else 'DESC',
        })

    def query(self, text, index):
        sort = []
        for i in self._sort:
            sort.append(' '.join(self._sort[i]))
        if sort:
            self.client.SetSortMode(sphinxapi.SPH_SORT_EXTENDED, ', '.join(sort))

        try:
            data = self.client.Query(text, index)
        except Exception:
            data = False

        if isinstance(data, bool) and not data:
            raise Exception('Searchd service error: ' + self.client.GetLastError())
        else:
            words = data['words'] if 'words' in data else []
            text = re.sub(r"[^-_\p{L}\p{N}]", ' ', text.lower())
            words.append(text.split(' '))
            data['words'] = set(word.strip(' \t-=+,.') for word in words)
            data['matches'] = data['matches'] if 'matches' in data else []

        return data

        # def get_items($searchword, $count, $offset, $sort, $fullSearch = false, $fillOffset = false):
        #     countProducts = 0
        #     result = {}
        #     index = 'patagraph_rt';
        #     self.client.ResetFilters()
        #     if sort:
        #         self.client.SetSelect("*,multiplier * @weight AS customweight")
        #
        #
        #
    #     if (!$countProducts){
    #     $this -> client -> ResetFilters();
    #     if ($sort){
    #     $this -> client -> SetSelect("*,multiplier * @weight AS customweight");
    #     $this -> sortedBy('sellStatus', false);
    #     if (key($sort) == '@relevance') {
    #     $this -> sortedBy('customweight', false);
    #     } else {
    #     $this -> sortedBy(key($sort), reset($sort));
    #     }
    #     }
    #
    #     if ($fullSearch) {
    #     $this -> client -> SetLimits(0, 100000);
    #     } else {
    #     $this -> client -> SetLimits($offset, $count + 1);
    #     }
    #
    #     if ($i = Yii::app() -> options -> sphinxWeightsForProducts){
    #     $this -> client -> SetFieldWeights($i);
    #     }
    #
    # $searchword = $this -> filterQueryString($searchword);
    # $data = $this -> Query($searchword, $index);
    # $countProducts = !empty($data['total_found']) ? $data['total_found']: 0;
    # }
    #
    # if ($countProducts) {
    # $allIds = array_keys($data['matches']);
    # }
    #
    # if ($countProducts){
    # $counts = $t2ids = array();
    # if ($fullSearch) {
    # / **
    # * @ var $facetService FacetService
    # * /
    # $facetService = ServiceFactory::
    #     get('Facet');
    # $ids = array_slice($allIds, $offset, $count + 1);
    # foreach($data['matches'] as $item) {
    #
    # $t2ids[ $item['attrs']['t2_1']] = true;
    # $t2ids[ $item['attrs']['t2_2']] = true;
    # $facetId = is_numeric( $item['attrs']['facetid'] ) ? $facetService -> getFacetIdByIntegerId($item['attrs'][
    #     'facetid']): $item['attrs']['facetid'];
    #
    # if (empty($counts[$facetId][$item['attrs']['t2_1']][$item['attrs']['t2_2']])){
    # $counts[$facetId][$item['attrs']['t2_1']][$item['attrs']['t2_2']] = 0;
    # }
    # $counts[$facetId][$item['attrs']['t2_1']][$item['attrs']['t2_2']]++;
    #
    # }
    # } else {
    # $ids = $allIds;
    # }
    #
    # $result = array(
    #     'more' = > count($ids) > $count,
    #                               'words' = > $data['words'],
    #                                            'counts' = > array('tree' = > $counts, 't2ids' = > array_keys($t2ids)),
    # 'all-ids' = > $allIds,
    #                'total-count' = > $countProducts,
    #                                   'current-ids' = > array_slice($ids, 0, $count),
    # );
    # }
    #
    # return $result;
    # }
