// Package pycymbal provides a simplified Go API for Python bindings
package pycymbal

import (
	"fmt"
	
	"github.com/1broseidon/cymbal/index"
)

// PythonCymbal provides a simplified API for Python
type PythonCymbal struct {
	dbPath string
}

// SymbolResult represents a code symbol found during indexing
type SymbolResult struct {
	Name      string
	Kind      string
	File      string
	StartLine int
	EndLine   int
	Language  string
}

// RefResult represents a reference to a symbol
type RefResult struct {
	File    string
	Line    int
	RelPath string
	Name    string
}

// InvestigateResult contains detailed information about a symbol
type InvestigateResult struct {
	Symbol     SymbolResult
	Source     string
	Kind       string
	Refs       []RefResult
	Impact     []ImpactResult
	Members    []SymbolResult
	Outline    []SymbolResult
}

// ImpactResult represents a symbol impacted by changes
type ImpactResult struct {
	Symbol   SymbolResult
	Reason   string
	Severity int
}

// NewCymbal creates a new PythonCymbal instance
func NewCymbal() *PythonCymbal {
	return &PythonCymbal{}
}

// Index indexes a repository and returns statistics
func (c *PythonCymbal) Index(repoPath string) (string, error) {
	stats, err := index.Index(repoPath, "", index.Options{})
	if err != nil {
		return "", err
	}
	c.dbPath, _ = index.RepoDBPath(repoPath)
	return fmt.Sprintf("Indexed %d files, found %d symbols", stats.FilesIndexed, stats.SymbolsFound), nil
}

// Search searches for symbols matching the query
func (c *PythonCymbal) Search(query string, limit int) ([]SymbolResult, error) {
	if c.dbPath == "" {
		return nil, fmt.Errorf("no database path set - call Index first")
	}
	results, err := index.SearchSymbols(c.dbPath, index.SearchQuery{
		Text:  query,
		Limit: limit,
	})
	if err != nil {
		return nil, err
	}

	wrapped := make([]SymbolResult, len(results))
	for i, r := range results {
		wrapped[i] = SymbolResult{
			Name:      r.Name,
			Kind:      r.Kind,
			File:      r.File,
			StartLine: r.StartLine,
			EndLine:   r.EndLine,
			Language:  r.Language,
		}
	}
	return wrapped, nil
}

// Investigate investigates a specific symbol
func (c *PythonCymbal) Investigate(symbolName string, fileHint string) (*InvestigateResult, error) {
	if c.dbPath == "" {
		return nil, fmt.Errorf("no database path set - call Index first")
	}
	res, err := index.Investigate(c.dbPath, symbolName, index.InvestigateOpts{FileHint: fileHint})
	if err != nil {
		return nil, err
	}

	wrapped := &InvestigateResult{
		Symbol: SymbolResult{
			Name:      res.Symbol.Name,
			Kind:      res.Symbol.Kind,
			File:      res.Symbol.File,
			StartLine: res.Symbol.StartLine,
			EndLine:   res.Symbol.EndLine,
			Language:  res.Symbol.Language,
		},
		Source: res.Source,
		Kind:   res.Kind,
		Refs:   make([]RefResult, len(res.Refs)),
	}

	for i, r := range res.Refs {
		wrapped.Refs[i] = RefResult{
			File:    r.File,
			Line:    r.Line,
			RelPath: r.RelPath,
			Name:    r.Name,
		}
	}
	return wrapped, nil
}

// FindReferences finds references to a symbol
func (c *PythonCymbal) FindReferences(symbolName string, limit int) ([]RefResult, error) {
	if c.dbPath == "" {
		return nil, fmt.Errorf("no database path set - call Index first")
	}
	results, err := index.FindReferences(c.dbPath, symbolName, limit)
	if err != nil {
		return nil, err
	}

	wrapped := make([]RefResult, len(results))
	for i, r := range results {
		wrapped[i] = RefResult{
			File:    r.File,
			Line:    r.Line,
			RelPath: r.RelPath,
			Name:    r.Name,
		}
	}
	return wrapped, nil
}

// GetDBPath returns the current database path
func (c *PythonCymbal) GetDBPath() string {
	return c.dbPath
}

// SetDBPath sets the database path directly (for testing or reuse)
func (c *PythonCymbal) SetDBPath(path string) {
	c.dbPath = path
}
