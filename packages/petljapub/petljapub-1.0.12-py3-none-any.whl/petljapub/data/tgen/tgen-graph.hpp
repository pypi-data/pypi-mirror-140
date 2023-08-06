
vector<pair<int, int>> random_tree(int n, int deg = -1) {
  if (deg == -1)
    deg = n;
  vector<int> numChildren(n, 0);
  vector<pair<int, int>> edges;
  for (int i = 1; i <= n-1; i++) {
    while (true) {
      int parent = random_value(0, i-1);
      if (numChildren[parent] == deg)
        continue;
      edges.emplace_back(parent, i);
      numChildren[parent]++;
      break;
    }
  }
  return edges;
}

vector<pair<int, int>> random_connected_undirected_graph(int n, int m) {
  assert(n-1 <= m && m <= n*(n-1) / 2);
  cout << n << " " << m << endl;

  /*
  auto code = [](int i, int j) {
                return j*(j-1)/2 + i;
              };
  auto decode = [](int k) {
                  int j = 0;
                  while (j*(j+1)/2 <= k)
                    j++;
                  int i = k - (j * (j-1)) / 2;
                  return make_pair(i, j);
                };
  */
  
  // obavezno ukljucujemo sve grane jednog nasumicnog drveta (sto obezbedjuje povezanost)
  vector<pair<int, int>> tree = random_tree(n);

  if (m < n*(n-1) / 4) {
    cout << "Include " << m << " edges" << endl;
    set<pair<int, int>> include_edges(begin(tree), end(tree));
    while (include_edges.size() < m) {
      int j = random_value(0, n-1);
      int i = random_value(0, j);
      include_edges.emplace(i, j);
    }
    vector<pair<int, int>> graph(begin(include_edges), end(include_edges));
    return graph;
  } else {
    cout << "Exclude " << n*(n-1)/2 - m << " edges" << endl; 
    set<pair<int, int>> tree_edges(begin(tree), end(tree));
    set<pair<int, int>> exclude_edges;
    while (exclude_edges.size() < n*(n-1)/2 - m) {
      int j = random_value(0, n-1);
      int i = random_value(0, j);
      if (tree_edges.find(make_pair(i, j)) == tree_edges.end())
        exclude_edges.emplace(i, j);
    }
    vector<pair<int, int>> graph;
    for (int j = 1; j < n; j++)
      for (int i = 0; i < j; i++)
        if (exclude_edges.find(make_pair(i, j)) == exclude_edges.end())
          graph.emplace_back(i, j);
    return graph;
  }
}

// orijentise grane drveta u skladu sa datim korenom
vector<pair<int, int>> rooted_tree(const vector<pair<int, int>>& tree,
                                   int n, int root) {
  vector<pair<int, int>> result;
  result.reserve(tree.size());
  vector<vector<int>> nbr(n);
  for (const auto& p : tree) {
    nbr[p.first].push_back(p.second);
    nbr[p.second].push_back(p.first);
  }
  vector<bool> visited(n);
  stack<int> st;
  st.push(root);
  visited[root] = true;
  while (!st.empty()) {
    int c = st.top(); st.pop();
    for (int s : nbr[c])
      if (!visited[s]) {
        st.push(s);
        visited[s] = true;
        result.emplace_back(c, s);
      }
  }
  return result;
}

vector<pair<int, int>> random_connected_directed_graph(int n, int m, int root) {
  assert(n-1 <= m && m <= n*n);
  assert(0 <= root && root < n);
  cout << n << " " << m << endl;

  // da li je grana (i, j) iskljucena iz grafa
  vector<tuple<bool, int, int>> edges(n*n);
  for (int j = 0; j < n; j++)
    for (int i = 0; i < n; i++)
      edges[j*n + i] = make_tuple(true, i, j);

  // obavezno ukljucujemo sve grane jednog nasumicnog drveta (sto obezbedjuje povezanost)
  vector<pair<int, int>> tree = random_tree(n);
  vector<pair<int, int>> graph = rooted_tree(tree, n, root);
  for (const auto& p : graph) {
    int i, j;
    tie(i, j) = p;
    get<0>(edges[j*n + i]) = false;
  }
  // pomeramo grane drveta na pocetak niza
  auto b = begin(edges), e = end(edges);
  partition(b, e, [](const tuple<bool, int, int>& t) {return !get<0>(t); });


  // ukljucujemo dodatnih nasumicno odabranih m - n grana
  random_shuffle(next(b, n-1), e);
  int numEdges = n-1;
  auto it = next(b, n-1);
  while (numEdges < m) {
    if (get<1>(*it) != get<2>(*it)) {
      graph.emplace_back(get<1>(*it), get<2>(*it));
      numEdges++;
    }
    it++;
  }
  
  return graph;
}

vector<pair<int, int>> random_directed_graph(int n, int m,
                                             bool allow_loops = false) {
  int max = n*n-(allow_loops ? 0 : n);
  assert(0 <= m && m < max);
  vector<int> nodes(max);
  int k = 0;
  for (int i = 0; i < n; i++)
    for (int j = 0; j < n; j++)
      if (i != j)
        nodes[k++] = n*i+j;
  // random_shuffle is too slow - shuffle only to the initial part
  for (int i = 0; i < m; i++)
    swap(nodes[i], nodes[random_value(i, max-1)]);
  vector<pair<int, int>> graph(m);
  k = 0;
  for (int i = 0; i < m; i++)
    graph[k++] = make_pair(nodes[i] / n,  nodes[i] % n);
  return graph;
}

vector<pair<int, int>> random_directed_acyclic_graph(int n, int m) {
  vector<int> order(n);
  iota(begin(order), end(order), 0);
  random_shuffle(begin(order), end(order));
  vector<pair<int, int>> nodes(n*(n-1)/2);
  for (int j = 1; j < n; j++)
    for (int i = 0; i < j; i++) {
      nodes[j*(j-1)/2 + i] = make_pair(i, j);
    }
  // random_shuffle is too slow - shuffle only to the initial part
  for (int i = 0; i < m; i++)
    swap(nodes[i], nodes[random_value(i, nodes.size()-1)]);
  vector<pair<int, int>> result;
  for (int i = 0; i < m; i++)
    result.emplace_back(order[nodes[i].first], order[nodes[i].second]);
  return result;
}
